# Part III — Capstone Theory (Day‑2, AM)

## 5.1 Capstone Overview & Success Criteria
Goal: **CrewAI agent** uses a **Langflow** tool **through** the **Gateway**, with guardrails and observability. Prove: discoverable tool, agent call via gateway, one blocked/one allowed call, RBAC 200/403, logs show correlation/request ID + latency.

## 5.2 Architecture: Langflow + CrewAI + Gateway
- **Langflow:** visual builder; flows as HTTP endpoints (`/api/v1/run/{flow_id}`)
- **Adapter/Server:** bridges Langflow to an MCP tool
- **MCP Gateway:** registers adapter; enforces policy; exposes catalog
- **CrewAI Agent:** only calls the Gateway

```
CrewAI Agent → MCP Gateway → Adapter/Server → Langflow API → Adapter → Gateway → Agent
```

## 5.3 Setup & Prerequisites
Gateway on :4444 + JWT; Python 3.11+; Langflow & CrewAI installed.

## 5.4 Designing the Langflow Tool (I/O and API)
Input: `{ "text": "..." }`  
Output: `{ "summary": "...", "tokens": 123 }`

Run Langflow:
```bash
pip install langflow
langflow run --host 0.0.0.0 --port 7860
# POST http://localhost:7860/api/v1/run/<flow_id>
```

## 5.5 Exposing Langflow as an MCP Tool Server
Adapter must serve `/tools` (list) and `/call/<tool>` (invoke + normalize JSON). Register in the Gateway.

## 5.6 The CrewAI Agent Pattern
Define Agent + Task; call the Gateway (not Langflow) via a small wrapper.

## 5.7 Hardening
Guardrails (rate limiter + secrets/PII), RBAC (`lf.summarize` only for `analyst`), optional OBO, and observability (payload logging, OTEL → Phoenix).
