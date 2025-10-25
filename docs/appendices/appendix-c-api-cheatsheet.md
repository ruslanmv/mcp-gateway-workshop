# Appendix C — API Usage Cheatsheet

```bash
export BASE_URL="http://localhost:4444"
export TOKEN="$MCPGATEWAY_BEARER_TOKEN"

# Health
curl -s $BASE_URL/health | jq '.'

# Register MCP server
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{
  "name":"my-mcp-server","url":"http://localhost:9000","description":"My custom MCP server","enabled":true,"request_type":"STREAMABLEHTTP"
}' $BASE_URL/gateways | jq '.'

# List tools
curl -s -H "Authorization: Bearer $TOKEN" $BASE_URL/tools | jq '.[] | {name: .name, gateway: .gatewaySlug}'
```

> Some builds expose `/tools/<tool-id>/invoke` instead of `/call/<name>`. Inspect tool details and adjust.
