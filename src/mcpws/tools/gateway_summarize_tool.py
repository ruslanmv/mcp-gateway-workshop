from typing import Optional
from crewai.tools import BaseTool
from ..utils.gateway_client import GatewayClient

class GatewaySummarizeTool(BaseTool):
    name: str = "GatewaySummarize"
    description: str = "Summarize text via MCP Gateway tool lf.summarize"

    def _run(self, text: str, run_manager: Optional[object] = None) -> str:  # type: ignore[override]
        gw = GatewayClient()
        res = gw.invoke("lf.summarize", {"text": text})
        return res.get("summary", "")
