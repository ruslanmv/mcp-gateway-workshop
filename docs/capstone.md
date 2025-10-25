# Capstone — CrewAI + Langflow via MCP Gateway

**Goal:** A CrewAI agent calls a Langflow tool through the MCP Gateway with guardrails, RBAC, and traces.

---

## A) Setup & Prereqs

```bash
# Gateway (if not already running)
mcpgateway --host 0.0.0.0 --port 4444

# Venv
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install langflow crewai fastapi uvicorn requests pydantic
```

**Verify gateway:**

```bash
curl -s http://localhost:4444/health | jq .
```

---

## B) Build the Langflow Tool

Run Langflow:

```bash
langflow run --host 0.0.0.0 --port 7860
```

Create a **Summarizer** flow:

- **Input:** `{ "text": "..." }`
- **Output:** `{ "summary": "..." }`  
  (If your flow returns chat-style output, we’ll normalize it in the adapter.)

**Test the flow (adjust `<flow_id>`):**

```bash
curl -s -X POST http://localhost:7860/api/v1/run/<flow_id>   -H 'Content-Type: application/json'   -d '{"input_value":"MCP Gateway centralizes tool governance...","input_type":"chat","output_type":"chat"}' | jq .
```

**Expected:** A nested JSON with the generated text inside `outputs[].outputs[].results.message.text`.

---

## C) Expose as an MCP Tool Server (Adapter)

```python
# langflow_adapter.py
from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()
LANGFLOW_URL = "http://localhost:7860/api/v1/run/<flow_id>"

@app.get("/tools")
def tools():
    return {"tools":[{"name":"lf.summarize","schema":{
        "type":"object","properties":{"text":{"type":"string"}},
        "required":["text"]}}]}

@app.post("/call/lf.summarize")
def call(payload: dict):
    try:
        body = {
          "input_value": payload.get("text", ""),
          "input_type": "chat",
          "output_type": "chat"
        }
        r = requests.post(LANGFLOW_URL, json=body, timeout=60)
        r.raise_for_status()
        data = r.json()
        # Extract nested message text from Langflow
        summary = (
          data.get("outputs", [{}])[0]
              .get("outputs", [{}])[0]
              .get("results", {})
              .get("message", {})
              .get("text", "")
        )
        return {
          "summary": summary,
          "tokens": (data.get("usage") or {}).get("total_tokens", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
```

**Run the adapter:**

```bash
uvicorn langflow_adapter:app --port 9100
```

**Register with Gateway:**

```bash
export BASE_URL=http://localhost:4444
export TOKEN=$MCPGATEWAY_BEARER_TOKEN

curl -s -X POST -H "Authorization: Bearer $TOKEN"   -H 'Content-Type: application/json'   -d '{
    "name": "langflow",
    "url": "http://localhost:9100",
    "description": "Langflow Summarizer",
    "enabled": true,
    "request_type": "STREAMABLEHTTP"
  }'   $BASE_URL/gateways | jq '.'
```

**Validate catalog:**

```bash
curl -s -H "Authorization: Bearer $TOKEN" $BASE_URL/tools | jq '.[] | {name, gateway: .gatewaySlug}'
```

### ✅ Solution

- `lf.summarize` visible in catalog; a test call returns a non-empty `"summary"`.

---

## D) CrewAI Agent

```python
# crew_agent_direct.py
from crewai import Agent, Task, Crew
import requests

GATEWAY = "http://localhost:4444"
TOOL = "lf.summarize"

def gateway_invoke(text: str):
    resp = requests.post(f"{GATEWAY}/call/{TOOL}", json={"text": text}, timeout=60)
    resp.raise_for_status()
    return resp.json()

analyst = Agent(role="Analyst", goal="Summarize via gateway-managed tools", backstory="Policy-first")
task = Task(description="Summarize: {text}", expected_output="A concise summary", agent=analyst)
crew = Crew(agents=[analyst], tasks=[task])

if __name__ == "__main__":
    result = gateway_invoke("MCP Gateway centralizes governance for AI tools...")
    print("Summary:", result.get("summary"))
```

### ✅ Solution

- Running the script prints a concise summary string.

---

## E) Guardrails (Rate Limit + Secrets)

```yaml
plugins:
  - name: rate_limiter
    kind: plugins.rate_limiter.rate_limiter.RateLimiterPlugin
    hooks: ["prompt_pre_fetch", "tool_pre_invoke"]
    mode: enforce
    priority: 50
    config:
      by_user: "3/10s"
      by_tool: "3/10s"
      burst: 1

  - name: SecretsDetection
    kind: plugins.secrets_detection.secrets_detection.SecretsDetectionPlugin
    hooks: ["prompt_pre_fetch", "tool_post_invoke", "resource_post_fetch"]
    mode: enforce
    priority: 45
    config:
      detectors:
        patterns:
          openai_key: true
          slack_token: true
          private_key_block: true
          jwt_like: true
      redact: true
      redaction_text: "***REDACTED***"
      block_on_detection: true
      min_findings_to_block: 1
```

**Provoke rate-limit:**

```bash
for i in 1 2 3 4; do
  curl -s -H "Authorization: Bearer $MCPGATEWAY_BEARER_TOKEN"     -X POST $BASE_URL/call/lf.summarize     -H 'Content-Type: application/json'     -d '{"text":"spam me"}' | jq . || true
done
```

**Provoke secrets detection:**

```bash
curl -s -H "Authorization: Bearer $MCPGATEWAY_BEARER_TOKEN"   -X POST $BASE_URL/call/lf.summarize   -H 'Content-Type: application/json'   -d '{"text":"sk-live-THIS-IS-FAKE-KEY"}' | jq .
```

### ✅ Solution

- You observe **429** on burst; secrets detector blocks or redacts per config.

---

## F) RBAC (+ Optional OBO)

```yaml
rbac:
  roles:
    - name: admin
      allow_all: true
    - name: analyst
      allow_tools: ["lf.summarize"]
    - name: viewer
      allow_tools: []
```

**Create tokens:**

```bash
export ANALYST_TOKEN=$(python3 -m mcpgateway.utils.create_jwt_token   --username analyst@example.com --exp 10080 --secret my-test-key   --extra '{"role":"analyst"}')

export VIEWER_TOKEN=$(python3 -m mcpgateway.utils.create_jwt_token   --username viewer@example.com --exp 10080 --secret my-test-key   --extra '{"role":"viewer"}')
```

**Test:**

```bash
curl -s -H "Authorization: Bearer $ANALYST_TOKEN"   -X POST $BASE_URL/call/lf.summarize   -H 'Content-Type: application/json'   -d '{"text":"ok"}' | jq .

curl -s -H "Authorization: Bearer $VIEWER_TOKEN"   -X POST $BASE_URL/call/lf.summarize   -H 'Content-Type: application/json'   -d '{"text":"deny"}' | jq .
```

### ✅ Solution

- Analyst call **200**; Viewer call **403**.

---

## G) Observability

Enable OTEL + Phoenix and send one request. Inspect **correlation IDs**, **latency**, and **policy decisions** in traces and logs.

```bash
docker run -p 6006:6006 -p 4317:4317 arizephoenix/phoenix:latest
export OTEL_ENABLE_OBSERVABILITY=true
export OTEL_TRACES_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
mcpgateway --host 0.0.0.0 --port 4444
```

### ✅ Solution

- Phoenix shows a span for your tool call with timing; gateway logs show structured JSON with decisions.
