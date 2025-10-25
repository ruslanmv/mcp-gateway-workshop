
# Quickstart — Run the Gateway Locally

## 1) Install & Launch

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -U mcp-contextforge-gateway
mcpgateway --host 0.0.0.0 --port 4444
```

Health check:

```bash
curl -s http://localhost:4444/health | jq .
```

## 2) Token for Auth (JWT)

```bash
export MCPGATEWAY_BEARER_TOKEN=$(python3 -m mcpgateway.utils.create_jwt_token \
  --username admin@example.com --exp 10080 --secret my-test-key)
```

## 3) List Tools (MCP CLI)

```bash
mcp --server http://localhost:4444 tools list
```

## 4) (Optional) Phoenix Tracing

```bash
docker run -p 6006:6006 -p 4317:4317 arizephoenix/phoenix:latest
export OTEL_ENABLE_OBSERVABILITY=true
export OTEL_TRACES_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
mcpgateway
```
