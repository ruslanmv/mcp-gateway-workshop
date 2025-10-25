
# Labs — Day 1

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

## Lab 1 — Gateway Up + Well-Known (45m)

```bash
mcpgateway --host 0.0.0.0 --port 4444
curl -s http://localhost:4444/health | jq .
```

## Lab 2 — Register Your First MCP Server (45m)

```bash
export BASE_URL=http://localhost:4444
export TOKEN=$MCPGATEWAY_BEARER_TOKEN

curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "calc-server",
    "url": "http://localhost:9100/mcp",
    "description": "Calculator MCP server",
    "enabled": true,
    "request_type": "STREAMABLEHTTP"
  }' \
  $BASE_URL/gateways | jq '.'
```

## Lab 3 — Clients & CLI (35m)

```bash
mcp --server http://localhost:4444 tools list
mcp --server http://localhost:4444 tool call calc.add '{"a":2,"b":3}'
```

## Lab 4 — Simple Passthrough / Wrapper (35m)

Concept YAML (illustrative):

```yaml
name: httpbin-wrapper
routes:
  - name: httpbin-get
    method: GET
    upstream: https://httpbin.org/get
```

## Lab 5 — Guardrails Intro (30m)

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
