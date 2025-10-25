from fastapi import FastAPI, HTTPException, Request
import requests, time, uuid, os
from typing import Dict, Any

app=FastAPI(title="Langflow Adapter")
FLOW_URL=os.getenv("LANGFLOW_URL","http://localhost:7860/api/v1/run/<flow_id>")
TIMEOUT=float(os.getenv("LANGFLOW_TIMEOUT","60"))

@app.get("/tools")
def tools()->Dict[str,Any]:
  return {"tools":[{"name":"lf.summarize","description":"Summarize via Langflow","schema":{"type":"object","properties":{"text":{"type":"string"}},"required":["text"]}}]}

@app.post("/call/lf.summarize")
def call(payload:Dict[str,Any], request:Request)->Dict[str,Any]:
  start=time.time(); corr=request.headers.get("x-correlation-id",str(uuid.uuid4()))
  try:
    body={"input_value":payload.get("text",""),"input_type":"chat","output_type":"chat"}
    r=requests.post(FLOW_URL,json=body,timeout=TIMEOUT); r.raise_for_status()
    j=r.json()
    msg=(j.get("outputs",[{}])[0].get("outputs",[{}])[0].get("results",{}).get("message",{}).get("text",""))
    return {"summary":msg,"correlation_id":corr,"latency_ms":int((time.time()-start)*1000)}
  except Exception as e:
    raise HTTPException(status_code=502, detail=f"{corr}: {e}")
