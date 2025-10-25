from fastapi import FastAPI, HTTPException
from typing import Dict, Any

app = FastAPI(title="Calculator Demo Server", version="0.1.0")

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}

@app.get("/tools")
def tools() -> Dict[str, Any]:
    return {"tools": [{"name": "calc.add", "schema": {"type":"object","properties":{"a":{"type":"number"},"b":{"type":"number"}},"required":["a","b"]}}]}

@app.post("/call/calc.add")
def add(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        a = float(payload["a"])
        b = float(payload["b"])
    except Exception:
        raise HTTPException(status_code=400, detail="payload requires numeric 'a' and 'b'")
    return {"result": a + b}
