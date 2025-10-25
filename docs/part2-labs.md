# Part II — Day‑1 Labs (with Solutions)

> Canonical gateway port: **4444**. Use the built‑in token utility for demo JWTs.

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

---

## Lab 1 — Quickstart: Run the Gateway (≈45m)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -U mcp-contextforge-gateway
mcpgateway --host 0.0.0.0 --port 4444
```

Health:

```bash
curl -s http://localhost:4444/health | jq .
```

JWT:

```bash
export MCPGATEWAY_BEARER_TOKEN=$(python3 -m mcpgateway.utils.create_jwt_token   --username admin@example.com --exp 10080 --secret my-test-key)
```

### ✅ Solution
You should see a small JSON object from `/health`, typically `{"status":"ok"...}` (exact fields may vary). Keep this terminal open so you can watch gateway logs during subsequent labs.

---

## Lab 2 — Register Your First MCP Server (≈45m)

Create `calculator_server.py`:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

app = FastAPI(title="Calculator MCP Server")

class AddPayload(BaseModel):
    a: float = Field(..., description="First addend")
    b: float = Field(..., description="Second addend")

@app.get("/tools")
def tools():
    return {
        "tools": [
            {
                "name": "calc.add",
                "description": "Add two numbers",
                "schema": {
                    "type": "object",
                    "properties": {
                        "a": {"type":"number"},
                        "b": {"type":"number"}
                    },
                    "required": ["a","b"]
                }
            }
        ]
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

Run:

```bash
pip install fastapi uvicorn pydantic
python calculator_server.py
```

Test locally:

```bash
curl -s http://localhost:9100/tools | jq .
curl -s -X POST http://localhost:9100/call/calc.add -H 'Content-Type: application/json' -d '{"a":2,"b":3}' | jq .
```

Register with the gateway:

```bash
export BASE_URL="http://localhost:4444"; export TOKEN="$MCPGATEWAY_BEARER_TOKEN"
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{
  "name":"calc-server","url":"http://localhost:9100","description":"Calculator MCP server","enabled":true,"request_type":"STREAMABLEHTTP"
}' $BASE_URL/gateways | jq '.'
curl -s -H "Authorization: Bearer $TOKEN" $BASE_URL/tools | jq '.[] | {name, gateway: .gatewaySlug}'
```

### ✅ Solution
- `/tools` returns a list including **calc.add**.
- POST returns `{"result": 5}` for `a=2,b=3`.
- Gateway catalog now lists `calc.add` under your gateway slug.

---

## Lab 3 — Clients & CLI (35m)

```bash
mcp --server http://localhost:4444 tools list
mcp --server http://localhost:4444 tool call calc.add '{"a":2,"b":3}'
```

### ✅ Solution
The CLI returns **5**. If listing works but calling fails, re-check the JSON payload *matches the tool schema exactly* and that your server is still running.

---

## Lab 4 — Simple Passthrough / Wrapper (35m)

Create `httpbin_wrapper.py`:

```python
from fastapi import FastAPI, HTTPException
import requests, uvicorn

app = FastAPI(title="HTTPBin Wrapper Server")

@app.get("/tools")
def tools():
    return {
        "tools": [
            {
                "name":"httpbin.get",
                "description":"GET https://httpbin.org/get",
                "schema": {"type":"object","properties":{},"additionalProperties":False}
            }
        ]
    }

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

Run & register similar to Lab 2.

### ✅ Solution
Calling the tool via the gateway returns an httpbin JSON (headers, origin, URL). You’ve wrapped a public HTTP API as a first‑class tool.

---

## Lab 5 — Guardrails Intro (30m)

Enable a basic rate limiter in your gateway config:

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

Provoke:

```bash
for i in {1..5}; do
  mcp --server http://localhost:4444 tool call calc.add '{"a":1,"b":1}' || true
done
```

### ✅ Solution
Early calls return **200**; later ones return **429 Too Many Requests**. Gateway logs show which bucket tripped (by user, tool, or tenant).
