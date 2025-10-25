from unittest.mock import patch, MagicMock
from src.mcpws.agents.crew_agent import main

def test_agent_main_mocked(capsys):
    with patch("src.mcpws.utils.gateway_client.GatewayClient.list_tools") as lt,          patch("src.mcpws.utils.gateway_client.GatewayClient.invoke") as inv:
        lt.return_value = [{"name":"lf.summarize"}]
        inv.return_value = {"summary":"hello","tokens":5}
        main("test text")
        out = capsys.readouterr().out
        assert "SUMMARY: hello" in out
