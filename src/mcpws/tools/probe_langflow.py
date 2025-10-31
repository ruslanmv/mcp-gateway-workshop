"""
Probe Langflow Flow (Capstone helper)
-------------------------------------
Sends a chat-style payload to Langflow's /api/v1/run/<flow_id> and extracts
the assistant message text, which is the most common output shape.

Usage:
  python -m src.mcpws.tools.probe_langflow "Your text"
Env:
  LANGFLOW_FLOW_ID=<uuid>                         (preferred)
  LANGFLOW_BASE=http://127.0.0.1:7860
  LANGFLOW_URL=http://127.0.0.1:7860/api/v1/run/<flow_id>  (overrides both)
  TIMEOUT=60
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict

import requests  # type: ignore[import-untyped]


def _flow_url() -> str:
    override = os.getenv("LANGFLOW_URL")
    if override:
        return override
    base = os.getenv("LANGFLOW_BASE", "http://127.0.0.1:7860")
    flow_id = os.getenv("LANGFLOW_FLOW_ID", "<flow_id>")
    return f"{base.rstrip('/')}/api/v1/run/{flow_id}"


def _extract_chat_text(resp_json: Dict[str, Any]) -> str:
    """
    Typical Langflow chat output shape:
      {
        "outputs": [
          {
            "outputs": [
              {
                "results": {
                  "message": { "text": "..." }
                }
              }
            ]
          }
        ]
      }
    """
    try:
        return (
            resp_json.get("outputs", [{}])[0]
            .get("outputs", [{}])[0]
            .get("results", {})
            .get("message", {})
            .get("text", "")
        )
    except Exception:
        return ""


def main() -> int:
    url = _flow_url()
    text = sys.argv[1] if len(sys.argv) > 1 else "MCP Context Forge centralizes governance."
    timeout = float(os.getenv("TIMEOUT", "60"))

    payload = {"input_value": text, "input_type": "chat", "output_type": "chat"}

    try:
        r = requests.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
        j = r.json() if r.content else {}
        msg = _extract_chat_text(j)
        if msg:
            print(msg)
        else:
            # Fallback: print full JSON so humans can inspect unexpected shapes.
            print(json.dumps(j, indent=2, ensure_ascii=False))
        return 0
    except requests.HTTPError as e:  # type: ignore[attr-defined]
        sys.stderr.write(f"[probe_langflow] HTTP {e.response.status_code}: {e}\n")
        return 2
    except Exception as e:
        sys.stderr.write(f"[probe_langflow] ERROR: {e}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
