from crewai import Agent, Task, Crew
import requests, os

GATEWAY=os.getenv("GATEWAY_URL","http://localhost:4444")
TOKEN=os.getenv("GATEWAY_TOKEN","")
headers={"Content-Type":"application/json", **({"Authorization":f"Bearer {TOKEN}"} if TOKEN else {})}

def summarize(text:str)->str:
  r=requests.post(f"{GATEWAY}/call/lf.summarize",json={"text":text},headers=headers,timeout=60)
  r.raise_for_status()
  return r.json().get("summary","")

agent=Agent(role="Analyst", goal="Use the Gateway only.")
task=Task(description="Summarize: {text}", expected_output="<=120 words", agent=agent)

if __name__ == "__main__":
  print(Crew(agents=[agent], tasks=[task]).kickoff(inputs={"text": summarize("MCP Gateway centralizes governance across agents.")}))
