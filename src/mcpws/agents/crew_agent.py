import os
from typing import Optional
from ..utils.gateway_client import GatewayClient
from ..utils.logging import get_logger

LOG = get_logger("crew-agent")

# We make CrewAI optional for environments without it;
# the gateway call remains the core demo.
def main(text: Optional[str] = None) -> None:
    text = text or "MCP Gateway centralizes tool governance for AI agents."
    gw = GatewayClient(base_url=os.environ.get("GATEWAY_URL", "http://localhost:4444"))
    LOG.info("list_tools")
    tools = gw.list_tools()
    LOG.info(f"tools: {len(tools)}")
    # Call our capstone tool via the gateway
    result = gw.invoke("lf.summarize", {"text": text})
    print("SUMMARY:", result.get("summary"))
    print("TOKENS:", result.get("tokens"))

if __name__ == "__main__":
    main()
