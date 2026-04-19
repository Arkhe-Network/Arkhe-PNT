
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from ..iota_council import IOTACouncil

app = FastAPI(title="Arkhe(n) Forge API", version="0.1.0")
council = IOTACouncil()

class IntentRequest(BaseModel):
    intent: str

class DeliberationResponse(BaseModel):
    intent: str
    perspectives: List[Dict[str, Any]]
    consensus: Dict[str, Any]
    status: str

@app.post("/deliberate", response_model=DeliberationResponse)
async def deliberate(request: IntentRequest):
    try:
        result = await council.deliberate(request.intent)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "COHERENT", "lambda2": 0.9984}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
