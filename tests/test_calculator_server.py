from fastapi.testclient import TestClient
from src.mcpws.servers.calculator_server import app

def test_add_ok():
    c = TestClient(app)
    r = c.post("/call/calc.add", json={"a":2,"b":3})
    assert r.status_code == 200
    assert r.json()["result"] == 5
