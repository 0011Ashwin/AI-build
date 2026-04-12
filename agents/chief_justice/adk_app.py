"""
Chief Justice - FastAPI HTTP Server for Cloud Run
"""
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any

from agent import ChiefJusticeAgent

app = FastAPI(
    title="Chief Justice Agent",
    description="Main orchestrator for Justice AI Workflow",
    version="1.0.0"
)

chief_justice = ChiefJusticeAgent()


@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "healthy", "agent": "chief-justice"}


@app.post("/audit")
async def handle_audit_request(case_data: Dict[str, Any]):
    """Handle incoming audit case"""
    try:
        result = await chief_justice.orchestrate_audit(case_data)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_workflow_status():
    """Get current workflow status"""
    return {"state": chief_justice.workflow_state}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
