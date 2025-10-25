
# Capstone — CrewAI + Langflow via MCP Gateway

**Goal:** A CrewAI agent calls a Langflow tool through the MCP Gateway with guardrails, RBAC, and traces.

## A) Setup & Prereqs

```bash
# Gateway (if not already running)
mcpgateway --host 0.0.0.0 --port 4444

# Venv
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install langflow crewai fastapi uvicorn requests
```

## B) Build the Langflow Tool

Run Langflow:

```bash
langflow run --host 0.0.0.0 --port 7860
```

Create a **Summarizer** flow with input `{ "text": "..." }` and output `{ "summary": "..." }`.

Test the flow (adjust `flow_id`):

```bash
curl -s -X POST http://localhost:7860/api/v1/run/<flow_id> \
  -H 'Content-Type: application/json' \
  -d '{"text":"MCP Gateway centralizes tool governance..."}' | jq .
```

## C) Expose as an MCP Tool Server (Adapter)

```python
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
        r = requests.post(LANGFLOW_URL, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        return {"summary": data.get("summary", ""),
                "tokens": data.get("usage", {}).get("total_tokens", 0)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
```

Run the adapter:

```bash
uvicorn src.mcpws.adapters.langflow_adapter:app --port 9100
```

Register with Gateway:

```bash
export BASE_URL=http://localhost:4444
export TOKEN=$MCPGATEWAY_BEARER_TOKEN

curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "langflow",
    "url": "http://localhost:9100",
    "description": "Langflow Summarizer",
    "enabled": true,
    "request_type": "STREAMABLEHTTP"
  }' \
  $BASE_URL/gateways | jq '.'
```

## D) CrewAI Agent

```python
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

**Test tokens:** create JWTs with `role` claim `analyst` vs `viewer`. Expect **200** vs **403**.

## G) Observability

Enable OTEL + Phoenix, then trigger a call and inspect trace + logs (correlation IDs, latency, policy decisions).
