
# MCP Gateway Masterclass

<p align="center">
  <a href="https://www.python.org" target="_blank"><img src="https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white" alt="Python 3.11+" /></a>
  <a href="https://fastapi.tiangolo.com" target="_blank"><img src="https://img.shields.io/badge/fastapi-%F0%9F%9A%80-009688?logo=fastapi&logoColor=white" alt="FastAPI" /></a>
  <a href="https://www.docker.com" target="_blank"><img src="https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white" alt="Docker Ready" /></a>
  <a href="https://squidfunk.github.io/mkdocs-material/" target="_blank"><img src="https://img.shields.io/badge/docs-MkDocs%20Material-000000?logo=markdown" alt="MkDocs Material" /></a>
  <a href="LICENSE" target="_blank"><img src="https://img.shields.io/badge/license-Apache--2.0-green" alt="License" /></a>
</p>

<div align="center">
  <img src="docs/assets/images/mcp-wallpaper.jpg" alt="MCP Gateway" width="820"/>
</div>

---

## Purpose & Scope

**This repository is a from-zero-to-hero masterclass to build governed, production-grade agentic AI using the Model Context Protocol (MCP) Gateway.**

By the end you will:

- Run the **MCP Gateway** locally and (optionally) in a small cluster
- Register and **federate tools** from MCP servers and REST APIs
- Enforce **enterprise guardrails** (RBAC, rate limits, PII/Secrets filters, schema guards)
- Capture **observability** (structured logs, correlation IDs, OTEL → Phoenix)
- Deliver a full **capstone**: a **CrewAI** agent consuming a **Langflow** tool **via the Gateway**

> Workshop site (MkDocs): build locally with `mkdocs serve`

---

## What You’ll Build

- **Day 1** — Foundations & First Value  
  Gateway quickstart, register a sample server, use clients, simple wrappers, turn on rate-limits.
- **Day 2** — Capstone  
  **Langflow** flow → **Adapter** as an MCP tool server → Registered in **Gateway** → Used by a **CrewAI** agent → Guardrails, RBAC, and traces.

---

## Prerequisites

- **Python 3.11+**, **Docker** (optional), **git**, **curl/jq**, **VS Code**
- (Optional) **minikube**, **kubectl**, **Helm** for cluster demos

---

## Quick Start (Gateway locally)

```bash
# clone & enter
git clone https://github.com/ruslanmv/mcp-gateway-workshop
cd mcp-gateway-workshop

# create venv and install gateway (if not using Docker Compose)
python3 -m venv .venv && source .venv/bin/activate
pip install -U mcp-contextforge-gateway

# run gateway on port 4444
mcpgateway --host 0.0.0.0 --port 4444

# health
curl -s http://localhost:4444/health | jq .
```

**Generate a demo JWT** (7 days):

```bash
export MCPGATEWAY_BEARER_TOKEN=$(python3 -m mcpgateway.utils.create_jwt_token \
  --username admin@example.com --exp 10080 --secret my-test-key)
```

List tools via **MCP CLI** (if installed):

```bash
mcp --server http://localhost:4444 tools list
```

---

## Capstone in 90 Seconds (minimum path)

```bash
# 1) Run Langflow
pip install langflow
langflow run --host 0.0.0.0 --port 7860

# 2) Start the adapter
pip install fastapi uvicorn requests
uvicorn src.mcpws.adapters.langflow_adapter:app --port 9100

# 3) Register adapter with Gateway
export BASE_URL=http://localhost:4444
curl -s -X POST -H "Authorization: Bearer $MCPGATEWAY_BEARER_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"name":"langflow","url":"http://localhost:9100","enabled":true,"request_type":"STREAMABLEHTTP"}' \
  $BASE_URL/gateways | jq '.'

# 4) Run the CrewAI agent
python -m src.mcpws.agents.crew_agent
```

---

## Production‑Minded Patterns

* **Config hygiene**: `.env.example`, `configs/gateway/*.yaml`, environment‑driven settings  
* **Guardrails**: `plugins` config for `rate_limiter`, `secrets_detection`, `pii_filter`, `schema_guard`  
* **Observability**: JSON logs + OTEL exports (Phoenix)  
* **RBAC & OBO**: role claims in JWTs; optional on‑behalf‑of flow  
* **Portability**: Dockerfiles, `pyproject.toml`, `requirements.txt`

---

## Docs Locally

```bash
pip install mkdocs-material
mkdocs serve
# open http://127.0.0.1:8000
```

Build static site:

```bash
mkdocs build --strict
```

---

## Contributing

PRs welcome. Please open an issue with clear repro steps and proposed changes.

---

## License

Released under **Apache-2.0**. See [LICENSE](LICENSE).

---

## Acknowledgments

Created by **Ruslan Magaña**. For updates and related projects, visit **ruslanmv.com**.
