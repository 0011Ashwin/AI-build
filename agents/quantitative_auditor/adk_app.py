"""
Quantitative Auditor - FastAPI HTTP Server for Cloud Run
Lazy imports to prevent startup crashes
"""
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from typing import Dict, Any

app = FastAPI(title="Quantitative Auditor Agent", version="1.0.0")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "quantitative-auditor"}


@app.post("/analyze")
async def handle_analysis_request(case_data: Dict[str, Any]):
    try:
        from agent import QuantitativeAuditorAgent
        auditor = QuantitativeAuditorAgent()
        result = await auditor.analyze_case(case_data)
        return {"analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/calculate-dir")
async def calculate_dir(data: Dict[str, Any]):
    try:
        from agent import QuantitativeAuditorAgent
        auditor = QuantitativeAuditorAgent()
        result = await auditor._calculate_disparate_impact(data)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting Quantitative Auditor on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
