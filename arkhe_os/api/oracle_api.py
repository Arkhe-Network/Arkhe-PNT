from fastapi import FastAPI, Query
from typing import List, Dict
try:
    from arkhe_os.molecular_workshop.oracle import MolecularPublicOracle
except ImportError:
    pass # tests or module might import it directly

app = FastAPI(title="ARKHE Molecular Oracle")
oracle = None

def get_oracle():
    global oracle
    if oracle is None:
        oracle = MolecularPublicOracle()
    return oracle

@app.get("/query")
def query_property(prop: str = Query(...), low: float = Query(...), high: float = Query(...), limit: int = 100):
    o = get_oracle()
    results = o.query_by_property(prop, low, high, limit)
    return {"results": results, "count": len(results)}

@app.get("/nl_query")
def nl_query(thought: str):
    o = get_oracle()
    results = o.natural_language_query(thought)
    return {"thought": thought, "results": results}

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
