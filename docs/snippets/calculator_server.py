from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

app = FastAPI(title="Calculator MCP Server")

class AddPayload(BaseModel):
    a: float = Field(..., description="First addend")
    b: float = Field(..., description="Second addend")

@app.get("/tools")
def tools():
    return {
        "tools": [
            {
                "name": "calc.add",
                "description": "Add two numbers",
                "schema": {
                    "type": "object",
                    "properties": {"a":{"type":"number"},"b":{"type":"number"}},
                    "required": ["a","b"]
                }
            }
        ]
    }

@app.post("/call/calc.add")
def call_add(payload: AddPayload):
    try:
        return {"result": payload.a + payload.b}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9100)
