from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os

app = FastAPI(title="🜏 HLML LLM Middleware")

# Configuration for local LLM (e.g. llama.cpp)
LLM_URL = os.getenv("LLM_URL", "http://localhost:8080/completion")

class TacticRequest(BaseModel):
    goal: str
    context: str = ""

class TacticResponse(BaseModel):
    tactic: str
    confidence: float
    metadata: dict = {}

@app.post("/tactic_suggest", response_model=TacticResponse)
async def suggest_tactic(req: TacticRequest):
    """
    Bridges Lean 4 formal requests with heuristic suggestions from an LLM.
    """
    prompt = f"""
    [INST] You are a Lean 4 mathematical expert.
    The current proof goal is: {req.goal}
    Additional context: {req.context}
    Suggest the most efficient and correct tactic to discharge this goal.
    Output only the tactic code. [/INST]
    """

    try:
        # This assumes a llama.cpp or compatible server is running
        response = requests.post(LLM_URL, json={
            "prompt": prompt,
            "n_predict": 64,
            "temperature": 0.2
        }, timeout=10)

        if response.status_code == 200:
            suggestion = response.json().get('content', 'simp').strip()
            return TacticResponse(tactic=suggestion, confidence=0.85)
        else:
            # Fallback for mock/offline mode
            return TacticResponse(tactic="simp", confidence=0.3, metadata={"error": "LLM offline"})

    except Exception as e:
        # Fallback tactic if LLM service is unreachable
        return TacticResponse(tactic="exact", confidence=0.1, metadata={"error": str(e)})

@app.get("/health")
async def health():
    return {"status": "resonant", "bridge": LLM_URL}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
