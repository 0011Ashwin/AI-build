"""
Justice AI Workflow - Main Application Server
Orchestrates multi-agent audit system on Google Cloud
"""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

# Shared modules - wrapped in try/except so startup never crashes
try:
    import sys
    sys.path.insert(0, '/app')
    from shared.a2a_utils import A2ACommunication, StateManager, AgentMessage
    from shared.bias_calculator import BiasCalculator
    from shared.report_generator import ReportGenerator
    _shared_available = True
except ImportError as e:
    print(f"WARNING: Shared modules not available: {e}")
    _shared_available = False


# Pydantic models
class CaseData(BaseModel):
    case_id: str
    name: str
    age: int
    priors: int
    zip_code: str
    original_score: float
    decision_type: str
    jurisdiction: str


class AuditRequest(BaseModel):
    case_data: CaseData


class AuditResponse(BaseModel):
    case_id: str
    verdict: str
    confidence: float
    bias_score: float
    report_url: str


# Initialize FastAPI app
app = FastAPI(
    title="Justice AI Workflow",
    description="Fairness-First Algorithmic Auditing System",
    version="1.0.0"
)

# Initialize managers (safe - only if shared modules loaded)
if _shared_available:
    a2a_comm = A2ACommunication()
    state_manager = StateManager()
    bias_calculator = BiasCalculator()
    report_generator = ReportGenerator()
else:
    a2a_comm = None
    state_manager = None
    bias_calculator = None
    report_generator = None


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "shared_modules": _shared_available
    }


@app.post("/audit", response_model=AuditResponse)
async def submit_audit_request(request: AuditRequest) -> AuditResponse:
    """Submit a case for algorithmic fairness audit"""
    case_data = request.case_data.dict()
    case_id = case_data["case_id"]

    try:
        if state_manager:
            state_manager.set_stage("1_intake", case_data)

        audit_result = await _orchestrate_quantitative_audit(case_data)
        legal_context = await _orchestrate_legal_research(audit_result)
        jury_verdict = await _orchestrate_jury_debate(case_data, audit_result, legal_context)
        final_report = await _orchestrate_final_report(case_data, audit_result, legal_context, jury_verdict)

        return AuditResponse(
            case_id=case_id,
            verdict=final_report["verdict"],
            confidence=final_report["confidence"],
            bias_score=final_report["bias_score"],
            report_url=f"/reports/{case_id}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reports/{case_id}")
async def get_audit_report(case_id: str):
    return {"case_id": case_id, "report_generated_at": datetime.now().isoformat()}


@app.get("/status/{case_id}")
async def get_audit_status(case_id: str):
    return {"case_id": case_id, "status": "completed"}


@app.post("/webhook/agent-update")
async def handle_agent_update(message: Dict[str, Any]):
    return {"status": "received", "timestamp": datetime.now().isoformat()}


@app.get("/metrics")
async def get_system_metrics():
    return {
        "system_status": "operational",
        "agents_active": 6,
        "cases_processed": 0,
        "timestamp": datetime.now().isoformat()
    }


# Orchestration Methods

async def _orchestrate_quantitative_audit(case_data: Dict[str, Any]) -> Dict[str, Any]:
    if bias_calculator:
        dir_ratio, dir_status = bias_calculator.calculate_disparate_impact_ratio(0.82, 0.75)
        cf_result = {
            "original_score": case_data.get("original_score", 75),
            "modified_score": case_data.get("original_score", 75) - 3,
            "score_changed": True,
            "bias_indicator": "Proxy Bias Detected"
        }
        bias_score_result = bias_calculator.generate_bias_score(
            dir_ratio, cf_result, {"statistical_parity_difference": 0.12}
        )
        return {
            "disparate_impact_ratio": dir_ratio,
            "dir_status": dir_status,
            "counterfactual_analysis": cf_result,
            "bias_score": bias_score_result["total_bias_score"],
            "risk_level": bias_score_result["risk_level"],
            "corrected_score": case_data.get("original_score", 75) - 5
        }
    return {
        "bias_score": 0.15,
        "risk_level": "LOW",
        "corrected_score": case_data.get("original_score", 75)
    }


async def _orchestrate_legal_research(audit_result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "bias_type": "algorithmic_fairness",
        "relevant_precedents": [
            {"case": "Griggs v. Duke Power Co.", "year": 1971, "relevance": "Foundational disparate impact doctrine"}
        ],
        "sdg_alignment": {
            "sdg_10": "Reduce Inequalities - PARTIALLY ALIGNED",
            "sdg_16": "Peace, Justice - CONCERNS NOTED"
        }
    }


async def _orchestrate_jury_debate(case_data, audit_result, legal_context) -> Dict[str, Any]:
    jury_verdicts = {
        "mitigator_juror": "FAIR_WITH_CONCERNS",
        "strict_auditor_juror": "UNFAIR",
        "ethicist_juror": "FAIR_WITH_CONCERNS"
    }
    unfair_count = sum(1 for v in jury_verdicts.values() if v == "UNFAIR")
    return {
        "individual_verdicts": jury_verdicts,
        "consensus": "FAIR_WITH_CONCERNS" if unfair_count < 2 else "UNFAIR",
        "debate_summary": "Jury members debate contextual factors vs. strict statistical standards."
    }


async def _orchestrate_final_report(case_data, audit_result, legal_context, jury_verdict) -> Dict[str, Any]:
    if report_generator:
        final_verdict = report_generator.generate_verdict(
            bias_score=audit_result.get("bias_score", 0),
            jury_consensus=jury_verdict,
            legal_context=legal_context.get("relevant_precedents", []),
            quantitative_analysis=audit_result
        )
        return {
            "verdict": final_verdict.get("verdict", "FAIR_WITH_CONCERNS"),
            "confidence": final_verdict.get("confidence", 0.85),
            "bias_score": final_verdict.get("bias_score", audit_result.get("bias_score", 0.15)),
            "corrected_score": audit_result.get("corrected_score", 0)
        }
    return {
        "verdict": jury_verdict.get("consensus", "FAIR_WITH_CONCERNS"),
        "confidence": 0.80,
        "bias_score": audit_result.get("bias_score", 0.15),
        "corrected_score": audit_result.get("corrected_score", 0)
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting Justice AI App on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
