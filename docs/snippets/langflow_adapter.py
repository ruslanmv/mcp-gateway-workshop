from fastapi import FastAPI, HTTPException, Request
import time
import uuid
import requests
from typing import Dict, Any

app = FastAPI()
FLOW_URL = "http://localhost:7860/api/v1/run/<flow_id>"
TIMEOUT = 60.0


@app.get("/tools")
def tools():
    return {
        "tools": [
            {
                "name": "lf.summarize",
                "schema": {
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": ["text"],
                },
            }
        ]
    }


@app.post("/call/lf.summarize")
def call(payload: Dict[str, Any], request: Request) -> Dict[str, Any]:
    start = time.time()
    corr = request.headers.get("x-correlation-id", str(uuid.uuid4()))
    try:
        body = {
            "input_value": payload.get("text", ""),
            "input_type": "chat",
            "output_type": "chat",
        }
        r = requests.post(FLOW_URL, json=body, timeout=TIMEOUT)
        r.raise_for_status()
        j = r.json()
        msg = (
            j.get("outputs", [{}])[0]
            .get("outputs", [{}])[0]
            .get("results", {})
            .get("message", {})
            .get("text", "")
        )
        return {
            "summary": msg,
            "tokens": (j.get("usage") or {}).get("total_tokens", 0),
            "correlation_id": corr,
            "latency_ms": int((time.time() - start) * 1000),
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"{corr}: {e}")
