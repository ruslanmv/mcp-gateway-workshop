import os, time, requests
from typing import Any, Dict, List, Optional
from .logging import get_logger, correlation_id

LOG = get_logger("gateway-client")

class GatewayClient:
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None, timeout: int = 60):
        self.base_url = base_url or os.environ.get("GATEWAY_URL", "http://localhost:4444")
        self.token = token or os.environ.get("GATEWAY_TOKEN")
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def list_tools(self) -> List[Dict[str, Any]]:
        cid = correlation_id()
        t0 = time.time()
        url = f"{self.base_url}/tools"
        resp = requests.get(url, headers=self._headers(), timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        LOG.info("list_tools", extra={"extra": {"cid": cid, "latency_ms": int(1000*(time.time()-t0))}})
        return data

    def invoke(self, tool_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Prefer canonical /call/<toolName>; adjust if your gateway uses /tools/<id>/invoke
        cid = correlation_id()
        t0 = time.time()
        url = f"{self.base_url}/call/{tool_name}"
        resp = requests.post(url, json=payload, headers=self._headers(), timeout=self.timeout)
        if resp.status_code >= 400:
            LOG.error("invoke_failed", extra={"extra": {"cid": cid, "status": resp.status_code, "body": resp.text}})
        resp.raise_for_status()
        data = resp.json()
        LOG.info("invoke_ok", extra={"extra": {"cid": cid, "latency_ms": int(1000*(time.time()-t0))}})
        return data
