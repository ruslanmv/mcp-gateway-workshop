from fastapi import FastAPI, HTTPException
import requests, uvicorn

app = FastAPI(title="HTTPBin Wrapper Server")

@app.get("/tools")
def tools():
    return {
        "tools": [
            {
                "name":"httpbin.get",
                "description":"GET https://httpbin.org/get",
                "schema":{"type":"object","properties":{},"additionalProperties":False}
            }
        ]
    }

@app.post("/call/httpbin.get")
def call_httpbin():
    try:
        r = requests.get("https://httpbin.org/get", timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=9200)
