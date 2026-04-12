"""
Ethicist Juror - FastAPI HTTP Server for Cloud Run
"""
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from typing import Dict, Any

from agent import EthicistJurorAgent

app = FastAPI(
    title="Ethicist Juror Agent",
    description="Ethicist Juror - Human Impact & SDG Alignment",
    version="1.0.0"
)

ethicist = EthicistJurorAgent()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "ethicist-juror"}


@app.post("/evaluate")
async def handle_evaluation(case_context: Dict[str, Any]):
    """Handle case evaluation"""
    try:
        result = await ethicist.evaluate_case(case_context)
        return {"verdict": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
