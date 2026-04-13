"""
Mitigator Juror — Cloud Run HTTP wrapper.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

app = FastAPI(title="Mitigator Juror Agent", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

try:
    from agent import evaluate_contextual_fairness, render_mitigator_verdict, root_agent
    _ok = True
except Exception as e:
    print(f"WARNING: Agent import failed: {e}")
    _ok = False


@app.get("/health")
async def health():
    return {"status": "healthy", "agent": "mitigator_juror", "ready": _ok}


@app.post("/evaluate")
async def evaluate(case_context: Dict[str, Any]):
    """Evaluate case from the Mitigator (defense) perspective."""
    if not _ok:
        raise HTTPException(503, "Agent not available")
    try:
        analysis = evaluate_contextual_fairness(
            bias_score=case_context.get("bias_score", 0),
            disparate_impact_ratio=case_context.get("disparate_impact_ratio", 1.0),
            score_changed_by_proxy=case_context.get("score_changed_by_proxy", False),
            decision_type=case_context.get("decision_type", "General"),
        )
        verdict = render_mitigator_verdict(analysis["contextual_fairness_score"])
        return {
            "juror_id": "mitigator_juror",
            "role": "Defense/Contextual",
            **verdict,
            "contextual_analysis": analysis,
        }
    except Exception as e:
        raise HTTPException(500, str(e))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
