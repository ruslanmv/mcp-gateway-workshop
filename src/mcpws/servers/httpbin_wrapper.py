"""
HTTPBin Wrapper MCP Server
--------------------------
Exports a single MCP-style tool `httpbin.get` that returns the JSON payload
from https://httpbin.org/get (or a custom upstream via env).

Endpoints:
  - GET  /health
  - GET  /tools
  - POST /call/httpbin.get

Env:
  UPSTREAM_URL=https://httpbin.org/get
  TIMEOUT=20
  LOG_LEVEL=INFO
  PORT=9200
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from typing import Any, Dict

import requests  # type: ignore[import-untyped]
from fastapi import FastAPI, HTTPException, Request
import uvicorn

UPSTREAM_URL = os.getenv("UPSTREAM_URL", "https://httpbin.org/get")
TIMEOUT = float(os.getenv("TIMEOUT", "20"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
PORT = int(os.getenv("PORT", "9200"))

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(message)s",
)
log = logging.getLogger("httpbin_wrapper")


def jlog(event: str, **fields: Any) -> None:
    record = {"event": event, **fields}
    log.info(json.dumps(record, ensure_ascii=False))


app = FastAPI(title="HTTPBin Wrapper Server", version="1.0.0")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/tools")
def tools() -> Dict[str, Any]:
    """
    MCP-style tool registry endpoint.
    NOTE: Schema is intentionally empty (no inputs) to match the Day-1 lab.
    """
    return {
        "tools": [
            {
                "name": "httpbin.get",
                "description": f"GET {UPSTREAM_URL}",
                "schema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
            }
        ]
    }


@app.post("/call/httpbin.get")
def call_httpbin(request: Request) -> Dict[str, Any]:
    start = time.time()
    corr = request.headers.get("x-correlation-id", str(uuid.uuid4()))
    try:
        headers = {"x-correlation-id": corr}
        r = requests.get(UPSTREAM_URL, timeout=TIMEOUT, headers=headers)
        r.raise_for_status()
        data = r.json()
        latency_ms = int((time.time() - start) * 1000)
        jlog("httpbin.ok", corr=corr, latency_ms=latency_ms, status=r.status_code)
        return {
            "status": r.status_code,
            "json": data,
            "correlation_id": corr,
            "latency_ms": latency_ms,
        }
    except Exception as e:
        jlog("httpbin.err", corr=corr, error=str(e))
        raise HTTPException(status_code=502, detail=f"{corr}: {e}") from e


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
