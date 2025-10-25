# Labs — Day 1

> Canonical gateway port: **4444**. Use the built-in token utility for demo JWTs.

---

## Lab 0 — Environment Checks (20m)

```bash
docker --version && docker compose version
python3 --version
```

Clean slate:

```bash
docker compose down -v 2>/dev/null || true
docker system prune -f --volumes
```

**Outcome:** Docker and Python ready; no stray containers on lab ports.

---

## Lab 1 — Gateway Up + Well-Known (45m)

**Run & verify:**

```bash
mcpgateway --host 0.0.0.0 --port 4444
curl -s http://localhost:4444/health | jq .
```

!!! note
Keep the gateway terminal open so you can see logs across labs.

### ✅ Solution

- If `/health` returns a JSON blob with a healthy flag, you’re done.
- If the port is busy, choose another free port, but use **4444** for the rest of the workshop if possible.

---

## Lab 2 — Register Your First MCP Server (45m)

We’ll use a tiny **calculator server** (FastAPI). Save as `calculator_server.py`:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

app = FastAPI(title="Calculator MCP Server")

class AddPayload(BaseModel):
    a: float = Field(..., description="First addend")
    b: float = Field(..., description="Second addend")

@app.get("/tools")
def list_tools():
    return {
        "tools": [{
            "name": "calc.add",
            "description": "Add two numbers",
            "schema": {
                "type": "object",
                "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
                "required": ["a", "b"]
            }
        }]}
    }

@app.post("/call/calc.add")
def call_add(payload: AddPayload):
    try:
        return {"result": payload.a + payload.b}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9100)
```

**Run it:**

```bash
pip install fastapi uvicorn pydantic
python calculator_server.py
```

**Register with the gateway:**

```bash
export BASE_URL=http://localhost:4444
export TOKEN=$MCPGATEWAY_BEARER_TOKEN

curl -s -X POST -H "Authorization: Bearer $TOKEN"   -H "Content-Type: application/json"   -d '{
    "name":"calc-server",
    "url":"http://localhost:9100",
    "description":"Calculator MCP server",
    "enabled":true,
    "request_type":"STREAMABLEHTTP"
  }'   $BASE_URL/gateways | jq '.'
```

**Validate:**

```bash
curl -s -H "Authorization: Bearer $TOKEN" $BASE_URL/tools | jq '.[] | {name, gateway: .gatewaySlug}'
```

### ✅ Solution

- `calc.add` appears in the catalog.
- Direct call test:

  ```bash
  curl -s -X POST http://localhost:9100/call/calc.add     -H 'Content-Type: application/json'     -d '{"a":2,"b":3}' | jq .
  ```

  Expected: `{"result":5}`.

---

## Lab 3 — Clients & CLI (35m)

```bash
mcp --server http://localhost:4444 tools list
mcp --server http://localhost:4444 tool call calc.add '{"a":2,"b":3}'
```

### ✅ Solution

- Output should be `5` from the CLI.  
- If listing works but calls fail, check the JSON shape against the tool schema.

---

## Lab 4 — Simple Passthrough / Wrapper (35m)

Wrap `https://httpbin.org/get` as **`httpbin.get`**.

**Wrapper (`httpbin_wrapper.py`):**

```python
from fastapi import FastAPI, HTTPException
import requests, uvicorn

app = FastAPI(title="HTTPBin Wrapper Server")

@app.get("/tools")
def tools():
  return {"tools":[{"name":"httpbin.get","description":"GET https://httpbin.org/get",
    "schema":{"type":"object","properties":{},"additionalProperties":False}}]}

@app.post("/call/httpbin.get")
def call_httpbin():
  try:
    r = requests.get("https://httpbin.org/get", timeout=20)
    r.raise_for_status()
    return r.json()
  except Exception as e:
    raise HTTPException(status_code=502, detail=str(e))

if __name__=="__main__":
  uvicorn.run(app, host="0.0.0.0", port=9200)
```

**Run + register:** mirror Lab 2 steps (use port **9200** and name `httpbin-wrapper`).  
**Call via CLI** or curl through the gateway.

### ✅ Solution

- Response JSON from httpbin (headers, origin, URL) confirms success.
- If you get 502, check outbound internet from your machine.

---

## Lab 5 — Guardrails Intro (30m)

Enable a **rate limiter**:

```yaml
plugins:
  - name: rate_limiter
    kind: plugins.rate_limiter.rate_limiter.RateLimiterPlugin
    hooks: ["prompt_pre_fetch", "tool_pre_invoke"]
    mode: enforce
    priority: 50
    config:
      by_user: "60/m"
      by_tenant: "600/m"
      by_tool: "30/m"
      burst: 5
```

**Provoke:**

```bash
for i in {1..5}; do
  mcp --server http://localhost:4444 tool call calc.add '{"a":1,"b":1}' || true
done
```

### ✅ Solution

- First few calls **200**, later call **429 Too Many Requests**.
- If not firing, lower thresholds temporarily (e.g., `3/10s`) and retry.

---

### You’re ready for Day-2 (Capstone)!
