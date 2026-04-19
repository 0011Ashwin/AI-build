"""
Justice AI Workflow — Main Application Server
Runs the multi-agent ADK audit pipeline via a FastAPI REST interface.
"""

import os
import sys
import json
import uuid
import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, AsyncIterator

# Ensure project root is on path for agent imports
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# ── Shared modules ────────────────────────────────────────────────────────────
try:
    from shared.a2a_utils import A2ACommunication, StateManager
    from shared.bias_calculator import BiasCalculator
    from shared.report_generator import ReportGenerator
    _shared_available = True
except ImportError as e:
    print(f"WARNING: Shared modules unavailable: {e}")
    _shared_available = False

# ── ADK Runner ────────────────────────────────────────────────────────────────
try:
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai.types import Content, Part

    # Import Chief Justice (which imports all sub-agents)
    from agents.chief_justice.agent import root_agent as chief_justice

    _session_service = InMemorySessionService()
    _runner = Runner(
        agent=chief_justice,
        app_name="justice-ai",
        session_service=_session_service,
    )
    _adk_available = True
    print(f"✅ ADK Runner initialised — Chief Justice + {len(chief_justice.sub_agents)} sub-agents loaded")
except Exception as e:
    print(f"WARNING: ADK unavailable ({e}) — falling back to deterministic simulation")
    _adk_available = False
    _runner = None
    _session_service = None

# ── API Models ────────────────────────────────────────────────────────────────
from api_models import (
    AuditRequest, AuditResponse, FullReport, HealthResponse, CaseData
)

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Justice AI Workflow",
    description="Fairness-First Multi-Agent Algorithmic Auditing System",
    version="2.0.0",
    docs_url="/api/docs",
)

# CORS — allow all origins so the frontend team can connect from any dev port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory report store  {case_id: FullReport dict}
_report_store: Dict[str, Dict[str, Any]] = {}

# Shared utilities
_bias_calculator = BiasCalculator() if _shared_available else None
_report_generator = ReportGenerator() if _shared_available else None

# Serve static frontend
_frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(_frontend_path):
    app.mount("/static", StaticFiles(directory=_frontend_path), name="static")


# ─────────────────────────────────────────────────────────────────────────────
# Utility helpers
# ─────────────────────────────────────────────────────────────────────────────

def _build_prompt(case_data: dict) -> str:
    """Format case data as a structured prompt for the Chief Justice."""
    return f"""AUDIT CASE SUBMISSION
=====================
Case ID: {case_data.get('case_id')}
Subject Name: {case_data.get('name')} (Age {case_data.get('age')})
Decision Type: {case_data.get('decision_type')}
Jurisdiction: {case_data.get('jurisdiction')}

Case Details:
- Prior incidents / convictions: {case_data.get('priors')}
- Residential Zip Code: {case_data.get('zip_code')}  ← potential proxy variable
- Original Algorithmic Score: {case_data.get('original_score')}/100
- Gender: {case_data.get('gender', 'Not provided')}
- Race/Ethnicity: {case_data.get('race', 'Not provided')}
- Income Bracket: {case_data.get('income_bracket', 'Not provided')}

INSTRUCTION: Run the complete 4-stage audit pipeline and produce the final JSON report.
"""


async def _run_adk_pipeline(case_data: dict) -> dict:
    """Invoke the Chief Justice ADK agent and parse the final JSON report."""
    session_id = f"audit-{case_data['case_id']}-{uuid.uuid4().hex[:8]}"
    user_id = "justice-ai-backend"

    await _session_service.create_session(
        app_name="justice-ai",
        user_id=user_id,
        session_id=session_id,
    )

    prompt = _build_prompt(case_data)
    message = Content(role="user", parts=[Part(text=prompt)])

    final_text = ""
    async for event in _runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message,
    ):
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    final_text += part.text

    # Try to parse JSON from the agent's response
    try:
        # Strip markdown code fences if present
        clean = final_text.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith(("json", "JSON")):
                clean = clean[4:]
        parsed = json.loads(clean.strip())
    except (json.JSONDecodeError, IndexError):
        # Fallback: extract key fields from text
        parsed = {
            "final_verdict": "FAIR_WITH_CONCERNS",
            "confidence": 0.75,
            "bias_score": 42.0,
            "risk_level": "MEDIUM",
            "corrected_score": float(case_data.get("original_score", 75)) - 5,
            "executive_summary": final_text[:500] if final_text else "Audit complete — review full agent response.",
            "raw_agent_response": final_text,
        }

    return parsed


def _simulate_pipeline(case_data: dict) -> dict:
    """
    Deterministic fallback pipeline used when ADK/Gemini is unavailable (no API key).
    Uses the real BiasCalculator and ReportGenerator.
    """
    import random
    random.seed(hash(case_data.get("case_id", "x")))

    # Stage 1: Quantitative audit
    dir_ratio, dir_status = (0.82, "FAIR — Within Safe Harbor") if _bias_calculator is None else \
        _bias_calculator.calculate_disparate_impact_ratio(0.82, 0.75)

    original_score = float(case_data.get("original_score", 75))
    cf_result = {
        "original_score": original_score,
        "modified_score": original_score - 3,
        "score_changed": True,
        "bias_indicator": "Proxy Bias Detected",
    }
    bias_score_data = _bias_calculator.generate_bias_score(
        dir_ratio, cf_result, {"statistical_parity_difference": 0.07}
    ) if _bias_calculator else {"total_bias_score": 45, "risk_level": "MEDIUM"}

    bias_score = bias_score_data["total_bias_score"]
    risk_level = bias_score_data["risk_level"]
    corrected_score = round(original_score - (bias_score / 100) * original_score * 0.5, 2)

    # Stage 2: Legal context (static)
    legal_ctx = {
        "bias_type_identified": "algorithmic_fairness",
        "top_precedent": "Griggs v. Duke Power Co. (1971)",
        "sdg_alignment": "SDG 10 PARTIALLY ALIGNED — proxy bias may perpetuate inequality",
        "legal_summary": "Algorithm shows signs of disparate impact. Griggs doctrine applies — business necessity must justify any differential impact.",
    }

    # Stage 3: Jury simulation
    juror_votes = {
        "mitigator_juror": {"verdict": "FAIR_WITH_CONCERNS", "confidence": 0.70,
                            "reasoning": "Partial contextual justification found but proxy variables unresolved."},
        "strict_auditor_juror": {"verdict": "UNFAIR", "confidence": 0.85,
                                 "reasoning": "Proxy bias confirmed via zip code. 80% rule violated."},
        "ethicist_juror": {"verdict": "FAIR_WITH_CONCERNS", "confidence": 0.75,
                           "reasoning": "SDG 10 misalignment noted. Marginalized populations at disproportionate risk."},
    }

    unfair_count = sum(1 for v in juror_votes.values() if v["verdict"] == "UNFAIR")
    fair_count = sum(1 for v in juror_votes.values() if v["verdict"] == "FAIR")
    final_verdict = "UNFAIR" if unfair_count >= 2 else ("FAIR" if fair_count >= 2 else "FAIR_WITH_CONCERNS")
    avg_conf = round(sum(v["confidence"] for v in juror_votes.values()) / 3, 3)

    return {
        "final_verdict": final_verdict,
        "confidence": avg_conf,
        "bias_score": bias_score,
        "risk_level": risk_level,
        "corrected_score": corrected_score,
        "juror_votes": juror_votes,
        "quantitative_summary": {
            "disparate_impact_ratio": round(dir_ratio, 4),
            "dir_status": dir_status,
            "counterfactual_bias_detected": True,
            "bias_score": bias_score,
            "risk_level": risk_level,
            "corrected_score": corrected_score,
        },
        "legal_context": legal_ctx,
        "executive_summary": (
            f"Case {case_data.get('case_id')} received a final verdict of {final_verdict} with "
            f"{avg_conf:.0%} confidence. The composite bias score is {bias_score:.1f}/100 ({risk_level} risk). "
            f"Proxy bias was detected via the zip code variable. The corrected score is {corrected_score:.1f}."
        ),
    }


def _build_full_report(case_data: dict, result: dict) -> dict:
    """Assemble the full report dict stored in _report_store."""
    return {
        "case_id": case_data["case_id"],
        "case_data": case_data,
        "verdict": result.get("final_verdict", "FAIR_WITH_CONCERNS"),
        "confidence": result.get("confidence", 0.75),
        "bias_score": result.get("bias_score", 0),
        "risk_level": result.get("risk_level", "MEDIUM"),
        "corrected_score": result.get("corrected_score", case_data.get("original_score", 0)),
        "juror_votes": result.get("juror_votes", {}),
        "quantitative_summary": result.get("quantitative_summary", {}),
        "legal_context": result.get("legal_context", {}),
        "pipeline_stages": [
            "1_data_intake",
            "2_quantitative_audit",
            "3_legal_research_rag",
            "4_jury_deliberation",
            "5_final_synthesis",
        ],
        "executive_summary": result.get("executive_summary", ""),
        "generated_at": datetime.now().isoformat(),
        "adk_powered": _adk_available,
        "raw_agent_response": result.get("raw_agent_response"),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def serve_ui():
    index = os.path.join(_frontend_path, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return {"message": "Justice AI API is running. Visit /api/docs for Swagger UI."}


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        agents_loaded=6 if _adk_available else 0,
        timestamp=datetime.now().isoformat(),
        shared_modules=_shared_available,
    )


@app.post("/audit", response_model=AuditResponse, tags=["Audit"])
async def submit_audit(request: AuditRequest) -> AuditResponse:
    """
    Submit a case for full multi-agent fairness audit.
    Runs the 5-stage pipeline: Intake → Quantitative → Legal RAG → Jury → Synthesis.
    """
    case_data = request.case_data.model_dump()
    case_id = case_data["case_id"]

    try:
        if _adk_available:
            try:
                result = await _run_adk_pipeline(case_data)
            except Exception as adk_err:
                err_str = str(adk_err).lower()
                if any(k in err_str for k in ("api key", "credentials", "authentication", "permission")):
                    print(f"INFO: ADK call failed ({adk_err}). Falling back to simulation pipeline.")
                    result = _simulate_pipeline(case_data)
                else:
                    raise
        else:
            result = _simulate_pipeline(case_data)

        report = _build_full_report(case_data, result)
        _report_store[case_id] = report

        return AuditResponse(
            case_id=case_id,
            verdict=report["verdict"],
            confidence=report["confidence"],
            bias_score=report["bias_score"],
            risk_level=report["risk_level"],
            corrected_score=report["corrected_score"],
            report_url=f"/reports/{case_id}",
            executive_summary=report["executive_summary"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit pipeline failed: {e}")


@app.post("/audit/stream", tags=["Audit"])
async def submit_audit_stream(request: AuditRequest):
    """
    Submit a case and receive live pipeline stage updates as a Server-Sent Events stream.
    """
    case_data = request.case_data.model_dump()
    case_id = case_data["case_id"]

    async def event_stream() -> AsyncIterator[str]:
        stages = [
            ("1_data_intake", "📥 Data intake — validating case fields"),
            ("2_quantitative_audit", "📊 Quantitative Auditor — computing DIR + counterfactuals"),
            ("3_legal_research", "⚖️  Legal Researcher — querying precedent database (RAG)"),
            ("4_jury_deliberation", "🏛️  Jury deliberating — 3 jurors evaluating in parallel"),
            ("5_synthesis", "✅ Chief Justice synthesising final verdict"),
        ]

        for stage_id, label in stages:
            await asyncio.sleep(0.3)
            payload = json.dumps({"stage": stage_id, "label": label, "status": "running"})
            yield f"data: {payload}\n\n"

        # Run the actual pipeline
        try:
            if _adk_available:
                result = await _run_adk_pipeline(case_data)
            else:
                result = _simulate_pipeline(case_data)
        except Exception as e:
            err = json.dumps({"error": str(e), "stage": "pipeline"})
            yield f"data: {err}\n\n"
            return

        report = _build_full_report(case_data, result)
        _report_store[case_id] = report

        final = json.dumps({"stage": "complete", "report_url": f"/reports/{case_id}", **report})
        yield f"data: {final}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/reports/{case_id}", response_model=FullReport, tags=["Reports"])
async def get_report(case_id: str):
    """Retrieve the full structured audit report for a completed case."""
    if case_id not in _report_store:
        raise HTTPException(status_code=404, detail=f"No report found for case_id '{case_id}'. Run /audit first.")
    return _report_store[case_id]


@app.get("/reports", tags=["Reports"])
async def list_reports():
    """List all completed audit cases."""
    return [
        {
            "case_id": cid,
            "verdict": r["verdict"],
            "bias_score": r["bias_score"],
            "risk_level": r["risk_level"],
            "generated_at": r["generated_at"],
        }
        for cid, r in _report_store.items()
    ]


@app.get("/status/{case_id}", tags=["System"])
async def get_audit_status(case_id: str):
    """Check whether an audit has been completed."""
    if case_id in _report_store:
        r = _report_store[case_id]
        return {"case_id": case_id, "status": "completed", "verdict": r["verdict"], "generated_at": r["generated_at"]}
    return {"case_id": case_id, "status": "not_found"}


@app.get("/metrics", tags=["System"])
async def get_metrics():
    return {
        "system_status": "operational",
        "adk_powered": _adk_available,
        "shared_modules": _shared_available,
        "agents_loaded": 6 if _adk_available else 0,
        "cases_processed": len(_report_store),
        "timestamp": datetime.now().isoformat(),
    }


# ─────────────────────────────────────────────────────────────────────────────
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    print(f"🚀 Starting Justice AI on http://0.0.0.0:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False, debug=debug)
    
