# Preface: Why an AI Gateway Now

Agentic AI is exploding: multiple LLMs, tools, plug‑ins, and data sources. Without a **central control plane**, teams face key sprawl, inconsistent security, no audit trail, and repeated integrations. An **MCP Gateway** fixes this by becoming a **single entry point** where **agents discover and use tools**, while the platform team enforces:

- **Security:** RBAC, OAuth/JWT, optional mTLS  
- **Governance:** PII/Secrets filters, schema guards, rate limits  
- **Observability:** JSON logs and OpenTelemetry traces

This site takes you from **first run** to **production‑grade**, finishing with a capstone: a **CrewAI agent** securely calling a **Langflow** tool **through** the **MCP Gateway**, with guardrails and logs that prove it.

**What you’ll build and learn**

- Stand up an MCP Gateway locally (and optionally with Docker Compose)
- Register servers and **federate tools** into a single catalog
- Wrap Langflow as a **gateway‑managed tool** via a tiny adapter
- Write a **CrewAI** agent that uses the gateway (not raw services)
- Apply **guardrails** (rate limiters, secret/PII filters, schema guards)
- Enforce role‑based access with **RBAC** and optional **On‑Behalf‑Of (OBO)**
- Capture **logs & traces** for auditability and cost reporting
