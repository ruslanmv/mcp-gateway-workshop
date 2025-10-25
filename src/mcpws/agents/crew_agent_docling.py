"""
CrewAI Agent using Gateway Docling RAG
--------------------------------------
Wraps the gateway tool 'docling.query' as a CrewAI tool and lets the Analyst
agent answer questions over ingested documents.

Env:
  GATEWAY_URL=http://localhost:4444
  GATEWAY_TOKEN=<JWT> (optional)
"""

from __future__ import annotations

import os
import requests  # type: ignore[import-untyped]
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool


class GatewayRAGTool(BaseTool):
    name = "GatewayRAG"
    description = "Answer questions over ingested documents via docling.query"

    def _run(self, question: str) -> str:
        base = os.getenv("GATEWAY_URL", "http://localhost:4444").rstrip("/")
        token = os.getenv("GATEWAY_TOKEN", "")
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        r = requests.post(
            f"{base}/call/docling.query",
            json={"query": question, "k": 4},
            headers=headers,
            timeout=60,
        )
        r.raise_for_status()
        return r.json().get("answer", "")


rag_tool = GatewayRAGTool(name="GatewayRAG", description="Answer questions via docling.query")
analyst = Agent(
    role="Analyst",
    goal="Answer contract and policy questions accurately using the governed Gateway tools.",
    backstory="Follows policy and only uses MCP tools wired through the Gateway.",
    tools=[rag_tool],
)

task = Task(
    description="Q&A: {question}",
    expected_output="A precise, well-structured answer.",
    agent=analyst,
)


def main() -> int:
    crew = Crew(agents=[analyst], tasks=[task])
    out = crew.kickoff(inputs={"question": "What’s our renewal window?"})
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
