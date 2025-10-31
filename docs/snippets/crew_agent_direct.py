from crewai import Agent, Task, Crew
import os
import requests

GATEWAY = os.getenv("GATEWAY_URL", "http://localhost:4444")
TOOL = "lf.summarize"


def gateway_invoke(text: str):
    resp = requests.post(f"{GATEWAY}/call/{TOOL}", json={"text": text}, timeout=60)
    resp.raise_for_status()
    return resp.json()


analyst = Agent(
    role="Analyst",
    goal="Summarize via gateway-managed tools",
    backstory="Policy-first",
)

task = Task(
    description="Summarize: {text}",
    expected_output="A concise summary",
    agent=analyst,
)

crew = Crew(agents=[analyst], tasks=[task])

if __name__ == "__main__":
    result = gateway_invoke("MCP Context Forge centralizes governance for AI tools...")
    print("Summary:", result.get("summary"))
