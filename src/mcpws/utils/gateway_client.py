from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional

import requests  # type: ignore[import-untyped]

from .logging import get_logger, correlation_id


class GatewayClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        timeout: float = 60.0,
    ) -> None:
        # Ensure we always have a string before calling rstrip()
        # Pull env var out first to help mypy infer the type as 'str'
        default_url = os.getenv("GATEWAY_URL", "http://localhost:4444")
        self.base_url = (base_url or default_url).rstrip("/")
        self.token = token or os.getenv("GATEWAY_TOKEN", "")
        self.timeout = timeout
        self.log = get_logger("gateway-client")

    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json", "x-correlation-id": correlation_id()}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def list_tools(self) -> List[Dict[str, Any]]:
        r = requests.get(f"{self.base_url}/tools", headers=self._headers(), timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list):
            return data
        return []

    def invoke(self, tool: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        t0 = time.time()
        r = requests.post(
            f"{self.base_url}/call/{tool}",
            json=payload,
            headers=self._headers(),
            timeout=self.timeout,
        )
        r.raise_for_status()
        res = r.json() if r.content else {}
        self.log.info(
            "tool.invoke.ok",
            extra={"extra": {"tool": tool, "latency_ms": int((time.time() - t0) * 1000)}},
        )
        return res
