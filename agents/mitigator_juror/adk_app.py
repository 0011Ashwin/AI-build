"""
Mitigator Juror - FastAPI HTTP Server for Cloud Run
Lazy imports to prevent startup crashes
"""
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from typing import Dict, Any

app = FastAPI(title="Mitigator Juror Agent", version="1.0.0")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "mitigator-juror"}


@app.post("/evaluate")
async def handle_evaluation(case_context: Dict[str, Any]):
    try:
        from agent import MitigatorJurorAgent
        mitigator = MitigatorJurorAgent()
        result = await mitigator.evaluate_case(case_context)
        return {"verdict": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting Mitigator Juror on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
