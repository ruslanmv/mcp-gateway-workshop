
# Langflow — File Map for Instructors

Start/Health/Settings:
- `src/backend/base/langflow/main.py`
- `src/backend/base/langflow/server.py`
- `src/backend/base/langflow/settings.py`
- `src/backend/base/langflow/api/health_check_router.py`

Run/Flows:
- `src/backend/base/langflow/api/v1/flows.py`
- `src/backend/base/langflow/services/flow/flow_runner.py`
- `src/backend/base/langflow/interface/run.py`
- `src/backend/base/langflow/api/v1/chat.py`

MCP Integration (optional deep dive):
- `src/backend/base/langflow/api/v1/mcp.py`, `v1/mcp_projects.py`, `v1/mcp_utils.py`
- `src/backend/base/langflow/api/v2/mcp.py`
- `src/backend/base/langflow/api/utils/mcp/config_utils.py`
- `src/backend/base/langflow/services/auth/mcp_encryption.py`
