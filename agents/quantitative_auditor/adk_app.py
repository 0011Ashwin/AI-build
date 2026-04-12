"""
Quantitative Auditor - FastAPI HTTP Server for Cloud Run
"""
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from typing import Dict, Any

from agent import QuantitativeAuditorAgent

app = FastAPI(
    title="Quantitative Auditor Agent",
    description="Quantitative Bias Analysis Agent",
    version="1.0.0"
)

auditor = QuantitativeAuditorAgent()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "quantitative-auditor"}


@app.post("/analyze")
async def handle_analysis_request(case_data: Dict[str, Any]):
    """Handle case analysis request"""
    try:
        result = await auditor.analyze_case(case_data)
        return {"analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/calculate-dir")
async def calculate_dir(data: Dict[str, Any]):
    """Calculate Disparate Impact Ratio"""
    try:
        result = await auditor._calculate_disparate_impact(data)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
