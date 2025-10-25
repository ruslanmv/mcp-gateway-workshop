"""
Trace Probe (Gateway/OTEL helper)
---------------------------------
Invokes the gateway tool `lf.summarize` with a correlation ID header and prints
the JSON response. Useful for validating tracing/telemetry setups (e.g., Phoenix).

Usage:
  python -m src.mcpws.tools.trace_probe "trace me"
Env:
  GATEWAY_URL=http://localhost:4444
  GATEWAY_TOKEN=...   (optional JWT for RBAC-protected tools)
  TIMEOUT=60
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from typing import Any, Dict

import requests  # type: ignore[import-untyped]

DEFAULT_TOOL = os.getenv("GATEWAY_TOOL", "lf.summarize")


def main() -> int:
    base = os.getenv("GATEWAY_URL", "http://localhost:4444").rstrip("/")
    token = os.getenv("GATEWAY_TOKEN", "")
    timeout = float(os.getenv("TIMEOUT", "60"))
    text = sys.argv[1] if len(sys.argv) > 1 else "trace me"
    corr = str(uuid.uuid4())

    headers = {"Content-Type": "application/json", "x-correlation-id": corr}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        r = requests.post(
            f"{base}/call/{DEFAULT_TOOL}",
            json={"text": text},
            headers=headers,
            timeout=timeout,
        )
        r.raise_for_status()
        data: Dict[str, Any] = r.json() if r.content else {}
        print(json.dumps({"correlation_id": corr, "response": data}, indent=2, ensure_ascii=False))
        return 0
    except requests.HTTPError as e:  # type: ignore[attr-defined]
        sys.stderr.write(f"[trace_probe] HTTP {e.response.status_code}: {e}\n")
        return 2
    except Exception as e:
        sys.stderr.write(f"[trace_probe] ERROR: {e}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
