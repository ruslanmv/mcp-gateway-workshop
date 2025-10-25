
# CrewAI — File Map for Instructors

Core API (Agent/Task/Crew):
- `lib/crewai/src/crewai/agent.py`
- `lib/crewai/src/crewai/task.py`
- `lib/crewai/src/crewai/crew.py`

Tools (bridge to MCP):
- `lib/crewai/src/crewai/tools/base_tool.py`
- `lib/crewai/src/crewai/tools/mcp_tool_wrapper.py`
- `lib/crewai/src/crewai/tools/tool_calling.py`
- `lib/crewai/src/crewai/tools/tool_types.py`
- `lib/crewai/src/crewai/tools/tool_usage.py`

LLM Providers:
- `lib/crewai/src/crewai/llms/base_llm.py`
- `lib/crewai/src/crewai/llms/providers/*/completion.py`

Telemetry:
- `lib/crewai/src/crewai/telemetry/telemetry.py`
- `lib/crewai/src/crewai/telemetry/utils.py`

Tool pack (examples):
- `lib/crewai-tools/README.md`, `lib/crewai-tools/BUILDING_TOOLS.md`
