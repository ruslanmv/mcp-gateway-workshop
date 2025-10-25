import os, time, requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from ..utils.logging import get_logger, correlation_id

LOG = get_logger("langflow-adapter")
app = FastAPI(title="Langflow MCP Adapter", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LANGFLOW_URL = os.environ.get("LANGFLOW_URL", "http://localhost:7860/api/v1/run/REPLACE_FLOW_ID")
TIMEOUT = int(os.environ.get("TIMEOUT", "60"))

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}

@app.get("/tools")
def tools() -> Dict[str, Any]:
    # Advertise a single summarizer tool with simple JSON schema
    return {
        "tools": [{
            "name": "lf.summarize",
            "description": "Summarize input text using a Langflow flow",
            "schema": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"]
            }
        }]
    }

@app.post("/call/lf.summarize")
def call_summarize(payload: Dict[str, Any]) -> Dict[str, Any]:
    if "text" not in payload or not isinstance(payload.get("text"), str):
        raise HTTPException(status_code=400, detail="payload requires a 'text' string")
    cid = correlation_id()
    t0 = time.time()
    try:
        r = requests.post(LANGFLOW_URL, json={"text": payload["text"]}, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        # normalize common fields
        result = {
            "summary": data.get("summary") or data.get("output") or data.get("result") or "",
            "tokens": data.get("usage", {}).get("total_tokens", 0),
        }
        LOG.info("lf.summarize.ok", extra={"extra": {"cid": cid, "latency_ms": int(1000*(time.time()-t0))}})
        return result
    except Exception as e:
        LOG.error("lf.summarize.err", extra={"extra": {"cid": cid, "error": str(e)}})
        raise HTTPException(status_code=502, detail=f"Langflow call failed: {e}")
