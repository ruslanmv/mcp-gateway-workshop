# MCP Context Forge Workshop — `src/` Guide (Hands-on, step-by-step)

Welcome! This README is your **field guide** for everything under `src/` that you’ll run during the workshop. It maps each folder to a lab, shows the **exact commands** to execute, and explains how the pieces fit together for production-minded use.

> Uses the project’s `Makefile` + `uv` (no bare `pip`). If you haven’t yet:
>
> ```bash
> make install         # ensures Python ≥ 3.11, installs deps with uv
> make docs-serve      # optional: serve the docs locally
> ```

---

## Folder map

````

src/
└── mcpws/
├── adapters/                # Servers that adapt external systems into MCP tools
│   └── langflow_adapter.py        ← Day-2: wraps a Langflow flow as tool `lf.summarize`
│
├── agents/                  # Example agents that ONLY talk through the Gateway
│   ├── crew_agent.py              ← Day-2: CrewAI agent (uses gateway_summarize_tool)
│   └── crew_agent_docling.py      ← Appendix: CrewAI agent for Docling RAG
│
├── cli/                     # (Optional) tiny CLI entrypoint
│   └── mcpws_cli.py
│
├── servers/                 # MCP-style servers exposing /tools + /call/<tool>
│   ├── calculator_server.py       ← Day-1 Lab 2: `calc.add`
│   ├── httpbin_wrapper.py         ← Day-1 Lab 4: wrapper/passthrough (`httpbin.get`)
│   └── docling_mcp_server.py      ← Appendix: Docling + Chroma + watsonx.ai (`docling.*`)
│
├── tools/                   # Reusable helpers and “probe” scripts
│   ├── gateway_summarize_tool.py  ← CrewAI tool that hits Gateway `/call/lf.summarize`
│   ├── probe_langflow.py          ← Day-2 sanity check: call Langflow directly
│   ├── trace_probe.py              ← Day-2 tracing demo: set correlation IDs
│   └── chat_rag_client.py          ← Appendix: ask `docling.query` via Gateway
│
├── utils/
│   ├── gateway_client.py          ← Thin HTTP client used by examples
│   └── logging.py                  ← Minimal JSON logger
│
└── **init**.py

````

**Top-level that you’ll use a lot**

- `docker-compose.yml` – spin up **Langflow**, the **adapter**, optional **agent**, the **Gateway**, and **Phoenix** (tracing).
- `scripts/create_jwt.py` – mint demo JWTs.
- `scripts/seed_gateway.sh` – register adapter(s) with the Gateway.
- `configs/gateway/*.yaml,*.env` – rate-limits, secrets detection, RBAC, well-known, etc.

---

## Environment

```bash
# One-time (installs uv if missing, creates .venv and syncs deps)
make install

# Optional: activate for convenience (uv works without this)
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
````

Useful env vars while running examples:

```bash
export GATEWAY_URL=http://localhost:4444
export GATEWAY_TOKEN=$(uv run --with pyjwt -- python scripts/create_jwt.py \
  --sub admin@example.com --role analyst --secret dev-secret --exp 120)
```

> If your Gateway doesn’t require auth for local dev, omit `GATEWAY_TOKEN`.

---

## Day-1 Labs (Foundations)

### Lab 0 — Environment checks

```bash
docker --version && docker compose version
uv --version
python -V
```

### Lab 1 — Bring the Gateway up

If you’re using the containerized gateway from `docker-compose.yml`:

```bash
docker compose up -d gateway
curl -s http://localhost:4444/health | jq .
```

Or run the binary you prefer; the workshop assumes port **4444**.

### Lab 2 — Your first MCP server: **calculator**

1. Run the server:

```bash
uv run -- uvicorn src.mcpws.servers.calculator_server:app --port 9100
```

2. Register with the Gateway:

```bash
export TOKEN=$GATEWAY_TOKEN
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"calc-server","url":"http://localhost:9100","description":"Calculator MCP server","enabled":true,"request_type":"STREAMABLEHTTP"}' \
  $GATEWAY_URL/gateways | jq '.'

curl -s -H "Authorization: Bearer $TOKEN" $GATEWAY_URL/tools | jq '.[] | {name, gateway: .gatewaySlug}'
```

3. Call the tool through the Gateway:

```bash
curl -s -H 'Content-Type: application/json' \
  -d '{"a":2,"b":3}' $GATEWAY_URL/call/calc.add | jq .
```

### Lab 3 — Clients & CLI

* **Gateway client** (thin helper you can reuse):

  ```bash
  uv run -- python -m src.mcpws.utils.gateway_client --help
  ```
* **MCP CLI** (optional): `pip install mcp-cli` then:

  ```bash
  mcp --server http://localhost:4444 tools list
  mcp --server http://localhost:4444 tool call calc.add '{"a":2,"b":3}'
  ```

### Lab 4 — Wrapper / passthrough: **httpbin**

1. Run the wrapper:

```bash
uv run -- uvicorn src.mcpws.servers.httpbin_wrapper:app --port 9200
```

2. Register:

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"httpbin","url":"http://localhost:9200","description":"HTTPBin wrapper","enabled":true,"request_type":"STREAMABLEHTTP"}' \
  $GATEWAY_URL/gateways | jq '.'
```

3. Call:

```bash
curl -s $GATEWAY_URL/call/httpbin.get | jq '.args,.headers'
```

### Lab 5 — Guardrails (rate-limit + 429)

Enable the sample plugin config in `configs/gateway/plugins.yaml` (how you pass it depends on your Gateway distribution). Once enabled:

```bash
for i in {1..5}; do
  curl -s -H 'Content-Type: application/json' -d '{"a":1,"b":1}' \
    $GATEWAY_URL/call/calc.add | jq '.status?, .error?' || true
done
```

Expect some **429** responses once the limiter kicks in.

---

## Day-2 Capstone (Langflow → Adapter → Gateway → Agent)

### A) Setup & prereqs

Bring up Langflow + Gateway (compose makes this easy):

```bash
docker compose up -d langflow gateway
open http://localhost:7860    # build your flow visually
```

### B) Langflow flow + sanity check

Create a **Summarizer** flow in Langflow with a single text input and single text output.

Sanity check the endpoint shape (replace `<flow_id>`):

```bash
uv run -- python -m src.mcpws.tools.probe_langflow "MCP Context Forge centralizes governance."
# Configure LANGFLOW_URL/LANGFLOW_FLOW_ID in the script env or your shell
```

### C) Adapter: expose the flow as an MCP tool

Run the adapter that maps `lf.summarize` → your flow:

```bash
uv run -- uvicorn src.mcpws.adapters.langflow_adapter:app --port 9100
```

Register with the Gateway (or just `make seed` which calls `scripts/seed_gateway.sh`):

```bash
make seed
curl -s -H "Authorization: Bearer $GATEWAY_TOKEN" $GATEWAY_URL/tools \
  | jq '.[] | select(.name | contains("lf.summarize")) | {name, gateway: .gatewaySlug}'
```

### D) Agent: CrewAI via Gateway

* The CrewAI **tool** that talks to the Gateway is in `tools/gateway_summarize_tool.py`.
* A tiny agent wire-up is in `agents/crew_agent.py`.

Run:

```bash
uv run -- python -m src.mcpws.agents.crew_agent
```

You should see a concise summary produced **via the Gateway** (not calling Langflow directly).

### E) Guardrails & Secrets

Enable `configs/gateway/plugins.yaml` and (optionally) a secrets-detection plugin. Then try a call that would be blocked or redacted. Capture both an **allowed** and a **blocked** example for your demo proofs.

### F) RBAC

Use `configs/gateway/rbac.yaml`. Mint tokens for different roles:

```bash
# Analyst (allowed)
uv run --with pyjwt -- python scripts/create_jwt.py --sub analyst@example.com --role analyst --secret dev-secret --exp 120

# Viewer (blocked)
uv run --with pyjwt -- python scripts/create_jwt.py --sub viewer@example.com --role viewer --secret dev-secret --exp 120
```

Test both tokens against `/call/lf.summarize` (expect **200** vs **403**).

### G) Observability: Phoenix + correlation IDs

Bring up Phoenix:

```bash
docker compose up -d phoenix
```

Send a traced call (random correlation ID set in the script):

```bash
uv run -- python -m src.mcpws.tools.trace_probe
```

Open Phoenix at [http://localhost:6006](http://localhost:6006) and confirm spans/latency.

---

## Appendix — Multimodal RAG (Docling + watsonx.ai)

The **optional** Docling appendix runs a separate MCP server:

* Server: `servers/docling_mcp_server.py` exposes `docling.parse`, `docling.ingest`, `docling.query`
* Client: `tools/chat_rag_client.py` asks `docling.query` **through the Gateway**
* Agent: `agents/crew_agent_docling.py` wraps the gateway RAG call as a CrewAI tool

**Run the server:**

```bash
uv run -- uvicorn src.mcpws.servers.docling_mcp_server:app --port 9200
```

**Register with Gateway:**

```bash
curl -s -X POST -H "Authorization: Bearer $GATEWAY_TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"docling","url":"http://localhost:9200","description":"Docling RAG","enabled":true,"request_type":"STREAMABLEHTTP"}' \
  $GATEWAY_URL/gateways | jq '.'
```

**Ingest & ask via Gateway:**

```bash
# (Ingest by calling server endpoints directly, then query through gateway)
uv run -- python -m src.mcpws.tools.chat_rag_client "What is our escalation policy?"
```

> Set `WATSONX_*` env vars for watsonx.ai; set `USE_LOCAL_EMBEDDINGS=1` for local embedding fallback.

---

## Using the Docker images (optional shortcuts)

`docker-compose.yml` also defines build contexts for the **adapter** and **agent**:

```bash
# Build & start everything
docker compose up -d

# Just rebuild the adapter after code changes
docker compose build adapter && docker compose up -d adapter
```

The compose file also starts **Langflow** and **Phoenix** so you can test end-to-end quickly.

---

## Troubleshooting

* **429 Too Many Requests**: You hit the rate limiter. Back off or adjust `configs/gateway/plugins.yaml`.
* **403 Forbidden**: Your role isn’t allowed. Check `configs/gateway/rbac.yaml` and your JWT `role` claim.
* **Token errors**: Ensure you minted with the same secret your Gateway expects. With the bundled script:

  ```bash
  uv run --with pyjwt -- python scripts/create_jwt.py --sub me@example.com --role analyst --secret dev-secret --exp 120
  ```
* **Flow not found**: Verify `LANGFLOW_URL` includes the correct `<flow_id>`. Use `tools/probe_langflow.py`.
* **CORS** (when calling from a browser): Enable permissive CORS in your Gateway config during dev.
* **Ports busy**: Something else is on `4444`, `7860`, `9100`, `9200`, or `6006`. Stop the conflict or change ports.
* **Windows**: Run `make` from Git Bash or WSL for the scripts that expect Bash.

---

## What’s “production-minded” here?

* **Gateway as control plane**: all tools behind one choke point.
* **RBAC** and **guardrails** on the Gateway—not sprinkled in adapters/agents.
* **Correlation IDs** passed through for **tracing**.
* **Adapters** are thin, stateless, and replaceable.
* **Docs** mirror code and vice-versa—your team can copy/paste labs into CI checks for drift.

Have fun—and keep everything going **through the Gateway** 🚀

