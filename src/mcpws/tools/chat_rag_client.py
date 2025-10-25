"""
Gateway RAG Chat Client (Docling)
---------------------------------
Simple client that calls the gateway's docling.query tool.

Env:
  GATEWAY_URL=http://localhost:4444
  GATEWAY_TOKEN=<JWT> (optional if your gateway requires auth)

Usage:
  uv run -- python -m src.mcpws.tools.chat_rag_client "What is our refund policy?"
"""

from __future__ import annotations

import os
import sys
import requests  # type: ignore[import-untyped]


BASE_URL = os.getenv("GATEWAY_URL", "http://localhost:4444").rstrip("/")
TOKEN = os.getenv("GATEWAY_TOKEN", "")

HEADERS = {"Content-Type": "application/json"}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"


def ask(query: str, k: int = 4) -> dict:
    url = f"{BASE_URL}/call/docling.query"
    r = requests.post(url, json={"query": query, "k": k}, headers=HEADERS, timeout=60)
    r.raise_for_status()
    return r.json()


def main() -> int:
    question = sys.argv[1] if len(sys.argv) > 1 else "Summarize our SOW termination clause."
    resp = ask(question)
    print("\nAnswer:\n", resp.get("answer", ""))
    print("\nSources:", resp.get("sources", []))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
