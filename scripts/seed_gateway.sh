#!/usr/bin/env bash
set -euo pipefail
BASE_URL=${BASE_URL:-http://localhost:4444}
TOKEN=${TOKEN:-""}
if [ -z "$TOKEN" ]; then echo "Set TOKEN env with a valid bearer token"; exit 1; fi

echo "Registering MCP server 'langflow' at adapter http://localhost:9100 ..."
curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json"   -d '{"name":"langflow","url":"http://adapter:9100","description":"Langflow Summarizer","enabled":true,"request_type":"STREAMABLEHTTP"}'   $BASE_URL/gateways | jq '.' || true

echo "Listing tools:"
curl -s -H "Authorization: Bearer $TOKEN" $BASE_URL/tools | jq '.[] | {name: .name, gateway: .gatewaySlug}'
