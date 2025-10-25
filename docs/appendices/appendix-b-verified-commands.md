# Appendix B — Verified Commands & Config

Install & launch:
```bash
pip install mcp-contextforge-gateway
mcpgateway --host 0.0.0.0 --port 4444
curl -s http://localhost:4444/health | jq .
```

JWT:
```bash
export MCPGATEWAY_BEARER_TOKEN=$(python3 -m mcpgateway.utils.create_jwt_token   --username admin@example.com --exp 10080 --secret my-test-key)
```

Well-Known:
```bash
export WELL_KNOWN_ROBOTS_TXT=$'User-agent: *\nDisallow: /'
export WELL_KNOWN_SECURITY_TXT=$'Contact: security@example.com\nEncryption: https://example.com/pgp\nExpires: 2025-12-31T23:59:59Z'
export WELL_KNOWN_CUSTOM_FILES='{"ai.txt":"AI is used for tool orchestration"}'
export WELL_KNOWN_CACHE_MAX_AGE=7200
```

Observability + Phoenix:
```bash
export OTEL_ENABLE_OBSERVABILITY=true
export OTEL_TRACES_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
docker run -p 6006:6006 -p 4317:4317 arizephoenix/phoenix:latest
mcpgateway
```

Wrapper & Bridge:
```bash
python -m mcpgateway.wrapper --gatewayBaseUrl http://localhost:4444 --token "$MCPGATEWAY_BEARER_TOKEN"
python -m mcpgateway.translate --mode stdio-to-sse --sseBaseUrl http://localhost:4444 --token "$MCPGATEWAY_BEARER_TOKEN"
```

MCP CLI:
```bash
mcp --server http://localhost:4444 tools list
mcp --server http://localhost:4444 tool call calc.add '{"a":2,"b":3}'
mcp --server http://localhost:4444 /save session.json
```
