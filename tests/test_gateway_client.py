from unittest.mock import patch, MagicMock
from src.mcpws.utils.gateway_client import GatewayClient


def test_list_tools_mocked():
    gc = GatewayClient(base_url="http://fake")
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [{"name": "lf.summarize"}]
        mock_get.return_value = mock_resp
        tools = gc.list_tools()
        assert tools[0]["name"] == "lf.summarize"


def test_invoke_mocked():
    gc = GatewayClient(base_url="http://fake")
    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"summary": "ok", "tokens": 10}
        mock_post.return_value = mock_resp
        res = gc.invoke("lf.summarize", {"text": "hi"})
        assert res["summary"] == "ok"
