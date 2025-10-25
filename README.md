# MCP Gateway Masterclass — Workshop

Production-ready repository for the **MCP Gateway Masterclass** and **CrewAI + Langflow** capstone.
Includes book manuscript, labs, Python code (adapter, agent, utilities), and Docker/Compose for a local stack.

## Quickstart

```bash
git clone https://github.com/ruslanmv/mcp-gateway-workshop.git
cd mcp-gateway-workshop
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# run adapter (Langflow must be running separately on :7860; see docker-compose.yml)
uvicorn src.mcpws.adapters.langflow_adapter:app --reload --port 9100
```

## One-button stack (Compose)

```bash
docker compose up -d
# gateway:  http://localhost:4444
# langflow: http://localhost:7860
# adapter:  http://localhost:9100
# phoenix:  http://localhost:6006 (tracing UI)
```

> You’ll still need to register the adapter as an MCP server with the MCP Gateway (see `scripts/seed_gateway.sh`).

## Repo layout

- `src/mcpws/` — Python package: adapter, agent, tools, utils, CLI
- `configs/` — gateway base config, plugins, RBAC, observability
- `labs/` — Day-1 and Day-2 hands-on exercises
- `book/` — Kindle-ready manuscript and images (placeholders)
- `docker/` — Dockerfiles for adapter, agent; and base Python
- `scripts/` — helper scripts (JWT, seeding, logs, certs)
- `tests/` — pytest unit tests (mocked HTTP)
