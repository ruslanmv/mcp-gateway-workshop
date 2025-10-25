# Part IV — Capstone Build (Day‑2, PM Labs) — with Solutions

> By the end you’ll have a Langflow tool powered by **IBM watsonx.ai** (or your chosen LLM), exposed through the **MCP Gateway**, driven by a **CrewAI agent**, and wrapped with guardrails, RBAC, and traces.

## 6.1 Lab A — Setup & Prereqs (15m)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install langflow crewai fastapi uvicorn requests pydantic ibm-generative-ai python-dotenv
pip install mcp-contextforge-gateway
mcpgateway --host 0.0.0.0 --port 4444
export MCPGATEWAY_BEARER_TOKEN=$(python3 -m mcpgateway.utils.create_jwt_token --username admin@example.com --exp 10080 --secret my-test-key)
curl -s http://localhost:4444/health | jq .
langflow run --host 0.0.0.0 --port 7860
```

### ✅ Solution
- Gateway `/health` is OK  
- Langflow UI responds on **:7860**

---

## 6.2 Lab B — Build the Langflow Tool (40m)

Create a Summarizer flow (Chat Input → Prompt → LLM → Chat Output). Programmatic probe:

```python
# probe_langflow.py
import requests
FLOW_ID="<flow-uuid>"
url=f"http://127.0.0.1:7860/api/v1/run/{FLOW_ID}"
payload={"input_value":"MCP Gateway centralizes governance.","input_type":"chat","output_type":"chat"}
r=requests.post(url,json=payload,timeout=60); r.raise_for_status()
j=r.json()
msg=(j.get("outputs",[{}])[0].get("outputs",[{}])[0].get("results",{}).get("message",{}).get("text",""))
print("Summary:", msg)
```

### ✅ Solution
You should see a summarized string printed to the console. If empty, confirm your flow’s output node is **Chat Output** and the `input_type/output_type` match.

---

## 6.3 Lab C — Expose as MCP Tool Server (30m)

```python
# langflow_adapter.py
from fastapi import FastAPI, HTTPException, Request
import requests, time, uuid, os
from typing import Dict, Any
app=FastAPI(title="Langflow Adapter")
FLOW_URL=os.getenv("LANGFLOW_URL","http://localhost:7860/api/v1/run/<flow_id>")
TIMEOUT=float(os.getenv("LANGFLOW_TIMEOUT","60"))
@app.get("/tools")
def tools()->Dict[str,Any]:
  return {"tools":[{"name":"lf.summarize","description":"Summarize via Langflow","schema":{"type":"object","properties":{"text":{"type":"string"}},"required":["text"]}}]}
@app.post("/call/lf.summarize")
def call(payload:Dict[str,Any], request:Request)->Dict[str,Any]:
  start=time.time(); corr=request.headers.get("x-correlation-id",str(uuid.uuid4()))
  try:
    body={"input_value":payload.get("text",""),"input_type":"chat","output_type":"chat"}
    r=requests.post(FLOW_URL,json=body,timeout=TIMEOUT); r.raise_for_status()
    j=r.json()
    msg=(j.get("outputs",[{}])[0].get("outputs",[{}])[0].get("results",{}).get("message",{}).get("text",""))
    return {"summary":msg,"correlation_id":corr,"latency_ms":int((time.time()-start)*1000)}
  except Exception as e:
    raise HTTPException(status_code=502, detail=f"{corr}: {e}")
```

Run + register:

```bash
uvicorn langflow_adapter:app --port 9100
export BASE_URL=http://localhost:4444; export TOKEN=$MCPGATEWAY_BEARER_TOKEN
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{
  "name":"langflow","url":"http://localhost:9100","description":"Langflow Summarizer","enabled":true,"request_type":"STREAMABLEHTTP"
}' $BASE_URL/gateways | jq '.'
curl -s -H "Authorization: Bearer $TOKEN" $BASE_URL/tools | jq '.[] | {name, gateway: .gatewaySlug}'
```

### ✅ Solution
`lf.summarize` appears in the catalog and returns a summarized response when invoked via the Gateway.

---

## 6.4 Lab D — Build the CrewAI Agent (35m)

Direct call:

```python
# crew_agent_direct.py
from crewai import Agent, Task, Crew
import requests, os
GATEWAY=os.getenv("GATEWAY_URL","http://localhost:4444")
TOKEN=os.getenv("GATEWAY_TOKEN","")
headers={"Content-Type":"application/json", **({"Authorization":f"Bearer {TOKEN}"} if TOKEN else {})}
def summarize(text:str)->str:
  r=requests.post(f"{GATEWAY}/call/lf.summarize",json={"text":text},headers=headers,timeout=60); r.raise_for_status(); return r.json().get("summary","")
agent=Agent(role="Analyst", goal="Use the Gateway only.")
task=Task(description="Summarize: {text}", expected_output="<=120 words", agent=agent)
print(Crew(agents=[agent], tasks=[task]).kickoff(inputs={"text": summarize("MCP Gateway centralizes governance across agents.")}))
```

### ✅ Solution
The agent prints a final response that contains the summarized text (computed by the Gateway‑fronted Langflow tool).

---

## 6.5 Lab E — Guardrails in Action (30m)

```yaml
plugins:
  - name: rate_limiter
    kind: plugins.rate_limiter.rate_limiter.RateLimiterPlugin
    hooks: ["tool_pre_invoke"]
    mode: enforce
    priority: 50
    config: { by_user: "3/10s", by_tool: "3/10s", burst: 1 }
  - name: SecretsDetection
    kind: plugins.secrets_detection.secrets_detection.SecretsDetectionPlugin
    hooks: ["tool_post_invoke"]
    mode: enforce
    priority: 45
    config:
      detectors: { patterns: { private_key_block: true, jwt_like: true, openai_key: true } }
      redact: true
      redaction_text: "***REDACTED***"
      block_on_detection: true
      min_findings_to_block: 1
```

Provoke a 429 and a redaction:

```bash
for i in 1 2 3 4; do
  curl -s -H "Authorization: Bearer $MCPGATEWAY_BEARER_TOKEN" -X POST $BASE_URL/call/lf.summarize -H 'Content-Type: application/json' -d '{"text":"spam me"}' | jq . || true
done
curl -s -H "Authorization: Bearer $MCPGATEWAY_BEARER_TOKEN" -X POST $BASE_URL/call/lf.summarize -H 'Content-Type: application/json' -d '{"text":"sk-live-THIS-IS-FAKE-KEY"}' | jq .
```

### ✅ Solution
- Rate‑limit triggers **429** on the 4th call.
- Secrets detector either blocks or redacts depending on config. Logs show the policy decision.

---

## 6.6 Lab F — RBAC (+ Optional OBO) (30m)

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

Tokens + test:

```bash
export ANALYST_TOKEN=$(python3 -m mcpgateway.utils.create_jwt_token --username analyst@example.com --exp 10080 --secret my-test-key --extra '{"role":"analyst"}')
export VIEWER_TOKEN=$(python3 -m mcpgateway.utils.create_jwt_token --username viewer@example.com --exp 10080 --secret my-test-key --extra '{"role":"viewer"}')

curl -s -H "Authorization: Bearer $ANALYST_TOKEN" -X POST $BASE_URL/call/lf.summarize -H 'Content-Type: application/json' -d '{"text":"ok"}' | jq .
curl -s -H "Authorization: Bearer $VIEWER_TOKEN"  -X POST $BASE_URL/call/lf.summarize -H 'Content-Type: application/json' -d '{"text":"deny"}' | jq .
```

### ✅ Solution
- Analyst call returns **200**.
- Viewer call returns **403**. Gateway logs show RBAC evaluation.

---

## 6.7 Lab G — Observability Trace (20m)

Enable OTEL + Phoenix, then send a request with a correlation ID:

```python
# trace_probe.py
import requests, uuid, os
base=os.getenv("GATEWAY_URL","http://localhost:4444")
headers={"Content-Type":"application/json","x-correlation-id":str(uuid.uuid4())}
token=os.getenv("GATEWAY_TOKEN",""); 
if token: headers["Authorization"]=f"Bearer {token}"
r=requests.post(f"{base}/call/lf.summarize",json={"text":"trace me"},headers=headers,timeout=60)
r.raise_for_status(); print(r.json())
```

### ✅ Solution
Open Phoenix at **http://localhost:6006** and locate a span containing your correlation ID, with child spans for plugin hooks and the adapter call.

---

## 6.8 Team Demos & Rubric (20–30m)

- Discovery: show `lf.summarize` in the catalog  
- Agent run: CrewAI summarizes via Gateway  
- Guardrails: demonstrate a **429** and a normal **200**  
- RBAC: **200** (analyst) vs **403** (viewer)  
- Trace: show correlation ID and latency in Phoenix
