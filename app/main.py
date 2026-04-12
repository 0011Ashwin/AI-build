"""
Justice AI Workflow - Main Application Server
Orchestrates multi-agent audit system on Google Cloud
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import asyncio
import json
from datetime import datetime
import sys
sys.path.append('./shared')

from shared.a2a_utils import A2ACommunication, StateManager, AgentMessage
from shared.bias_calculator import BiasCalculator
from shared.report_generator import ReportGenerator


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

# Initialize managers
a2a_comm = A2ACommunication()
state_manager = StateManager()
bias_calculator = BiasCalculator()
report_generator = ReportGenerator()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.post("/audit", response_model=AuditResponse)
async def submit_audit_request(request: AuditRequest) -> AuditResponse:
    """
    Submit a case for algorithmic fairness audit
    
    This endpoint orchestrates the entire 5-state workflow:
    1. Intake Node - Collect data
    2. Audit Chamber - Quantitative analysis
    3. Contextual RAG - Legal research
    4. Jury Verdict - Multi-agent debate
    5. Mitigation & Reporting - Final verdict
    """
    case_data = request.case_data.dict()
    case_id = case_data["case_id"]
    
    try:
        # State 1: Intake
        state_manager.set_stage("1_intake", case_data)
        
        # State 2: Quantitative Audit
        audit_result = await _orchestrate_quantitative_audit(case_data)
        state_manager.set_stage("2_audit_chamber", audit_result)
        
        # State 3: Legal Research (RAG)
        legal_context = await _orchestrate_legal_research(audit_result)
        state_manager.set_stage("3_contextual_rag", legal_context)
        
        # State 4: Jury Debate
        jury_verdict = await _orchestrate_jury_debate(case_data, audit_result, legal_context)
        state_manager.set_stage("4_jury_verdict", jury_verdict)
        
        # State 5: Final Report
        final_report = await _orchestrate_final_report(
            case_data,
            audit_result,
            legal_context,
            jury_verdict
        )
        state_manager.set_stage("5_mitigation", final_report)
        
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
    """Retrieve audit report for a specific case"""
    full_context = state_manager.get_full_context()
    
    if case_id not in full_context.get("case_data", {}):
        raise HTTPException(status_code=404, detail="Case not found")
    
    return {
        "case_id": case_id,
        "workflow_state": full_context.get("workflow_state", {}),
        "report_generated_at": datetime.now().isoformat()
    }


@app.get("/status/{case_id}")
async def get_audit_status(case_id: str):
    """Get current audit status for a case"""
    return {
        "case_id": case_id,
        "status": "completed",
        "workflow_state": state_manager.get_full_context()
    }


# Orchestration Methods

async def _orchestrate_quantitative_audit(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """Orchestrate State 2: Quantitative Audit"""
    # Calculate Disparate Impact Ratio
    dir_ratio, dir_status = bias_calculator.calculate_disparate_impact_ratio(0.82, 0.75)
    
    # Simulate counterfactual analysis
    cf_result = {
        "original_score": case_data.get("original_score", 75),
        "modified_score": case_data.get("original_score", 75) - 3,
        "score_changed": True,
        "bias_indicator": "Proxy Bias Detected"
    }
    
    # Calculate bias score
    bias_score_result = bias_calculator.generate_bias_score(dir_ratio, cf_result, {
        "statistical_parity_difference": 0.12
    })
    
    return {
        "disparate_impact_ratio": dir_ratio,
        "dir_status": dir_status,
        "counterfactual_analysis": cf_result,
        "bias_score": bias_score_result["total_bias_score"],
        "risk_level": bias_score_result["risk_level"],
        "corrected_score": case_data.get("original_score", 75) - (bias_score_result["total_bias_score"] / 100 * case_data.get("original_score", 75))
    }


async def _orchestrate_legal_research(audit_result: Dict[str, Any]) -> Dict[str, Any]:
    """Orchestrate State 3: Legal Research & RAG"""
    return {
        "bias_type": "algorithmic_fairness",
        "relevant_precedents": [
            {
                "case": "Griggs v. Duke Power Co.",
                "year": 1971,
                "relevance": "Foundational disparate impact doctrine"
            }
        ],
        "sdg_alignment": {
            "sdg_10": "Reduce Inequalities - PARTIALLY ALIGNED",
            "sdg_16": "Peace, Justice - CONCERNS NOTED"
        }
    }


async def _orchestrate_jury_debate(
    case_data: Dict[str, Any],
    audit_result: Dict[str, Any],
    legal_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Orchestrate State 4: Jury Debate (Parallel Agents)"""
    # Simulate jury verdicts
    jury_verdicts = {
        "mitigator_juror": "FAIR_WITH_CONCERNS",
        "strict_auditor_juror": "UNFAIR",
        "ethicist_juror": "FAIR_WITH_CONCERNS"
    }
    
    # Determine consensus
    unfair_count = sum(1 for v in jury_verdicts.values() if v == "UNFAIR")
    
    return {
        "individual_verdicts": jury_verdicts,
        "consensus": "FAIR_WITH_CONCERNS" if unfair_count < 2 else "UNFAIR",
        "debate_summary": "Jury members debate contextual factors vs. strict statistical standards. Ethicist raises SDG concerns."
    }


async def _orchestrate_final_report(
    case_data: Dict[str, Any],
    audit_result: Dict[str, Any],
    legal_context: Dict[str, Any],
    jury_verdict: Dict[str, Any]
) -> Dict[str, Any]:
    """Orchestrate State 5: Final Report Generation"""
    # Generate final verdict
    final_verdict = report_generator.generate_verdict(
        bias_score=audit_result.get("bias_score", 0),
        jury_consensus=jury_verdict,
        legal_context=legal_context.get("relevant_precedents", []),
        quantitative_analysis=audit_result
    )
    
    # Generate PDF report
    pdf_report = report_generator.generate_pdf_report(
        case_data=case_data,
        verdict=final_verdict,
        quantitative_analysis=audit_result,
        legal_context=legal_context.get("relevant_precedents", []),
        jury_debate=jury_verdict
    )
    
    return {
        "verdict": final_verdict["verdict"],
        "confidence": final_verdict["confidence"],
        "bias_score": final_verdict["bias_score"],
        "corrected_score": audit_result.get("corrected_score", 0),
        "report": pdf_report["report_content"]
    }


@app.post("/webhook/agent-update")
async def handle_agent_update(message: Dict[str, Any]):
    """Webhook for agent-to-agent updates"""
    agent_msg = AgentMessage(
        sender_id=message.get("sender_id"),
        recipient_id=message.get("recipient_id"),
        message_type=message.get("message_type"),
        content=message.get("content")
    )
    a2a_comm.send_message(agent_msg)
    return {"status": "received", "message_id": agent_msg.timestamp}


@app.get("/metrics")
async def get_system_metrics():
    """Get system metrics and statistics"""
    return {
        "system_status": "operational",
        "agents_active": 6,
        "cases_processed": 0,
        "average_audit_time_ms": 0,
        "fairness_alerts": 0,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
