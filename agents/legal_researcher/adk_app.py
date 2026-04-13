"""
Legal Researcher — Cloud Run HTTP wrapper.
Exposes RAG-based legal precedent retrieval tools as REST endpoints.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

app = FastAPI(title="Legal Researcher Agent", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

try:
    from agent import (
        query_legal_precedents,
        check_sdg_alignment,
        retrieve_comparable_cases,
        query_sentencing_guidelines,
        root_agent,
    )
    _ok = True
except Exception as e:
    print(f"WARNING: Agent import failed: {e}")
    _ok = False


@app.get("/health")
async def health():
    return {"status": "healthy", "agent": "legal_researcher", "ready": _ok}


@app.post("/research")
async def research(audit_findings: Dict[str, Any]):
    """Run full legal research for identified bias findings."""
    if not _ok:
        raise HTTPException(503, "Agent not available")
    try:
        bias_type = audit_findings.get("bias_type", "algorithmic_fairness")
        precedents = query_legal_precedents(bias_type)
        sdg = check_sdg_alignment(bias_type)
        cases = retrieve_comparable_cases(f"{audit_findings.get('decision_type','general')} bias case")
        guidelines = query_sentencing_guidelines(
            audit_findings.get("jurisdiction", "US Federal"),
            audit_findings.get("decision_type", "Algorithmic Decision"),
        )
        return {
            "bias_type_identified": bias_type,
            "legal_precedents": precedents,
            "sdg_alignment": sdg,
            "comparable_cases": cases,
            "applicable_guidelines": guidelines,
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/tools/query-precedents")
async def tool_query_precedents(data: Dict[str, Any]):
    if not _ok:
        raise HTTPException(503, "Agent not available")
    return query_legal_precedents(data.get("bias_type", "algorithmic_fairness"), data.get("top_k", 3))


@app.post("/tools/sdg-alignment")
async def tool_sdg(data: Dict[str, Any]):
    if not _ok:
        raise HTTPException(503, "Agent not available")
    return check_sdg_alignment(data.get("bias_type", "algorithmic_fairness"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
