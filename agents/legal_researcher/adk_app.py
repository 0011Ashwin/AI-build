"""
Legal Researcher - FastAPI HTTP Server for Cloud Run
"""
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from typing import Dict, Any

from agent import LegalResearcherAgent

app = FastAPI(
    title="Legal Researcher Agent",
    description="Legal Research and Precedent Retrieval Agent",
    version="1.0.0"
)

researcher = LegalResearcherAgent()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "legal-researcher"}


@app.post("/research")
async def handle_research_request(audit_findings: Dict[str, Any]):
    """Handle legal research request"""
    try:
        result = await researcher.research_bias(audit_findings)
        return {"research_result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/query-precedents")
async def query_precedents(data: Dict[str, Any]):
    """Query legal precedents"""
    try:
        result = await researcher._query_precedents(data.get("bias_type", ""))
        return {"precedents": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
