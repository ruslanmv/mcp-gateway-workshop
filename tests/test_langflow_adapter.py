from fastapi.testclient import TestClient
from src.mcpws.adapters.langflow_adapter import app

def test_health():
    c = TestClient(app)
    r = c.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_tools():
    c = TestClient(app)
    r = c.get("/tools")
    assert r.status_code == 200
    assert "tools" in r.json()
