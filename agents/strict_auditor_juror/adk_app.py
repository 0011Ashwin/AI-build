"""
Strict Auditor Juror — Cloud Run HTTP wrapper.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List

app = FastAPI(title="Strict Auditor Juror Agent", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

try:
    from agent import identify_bias_red_flags, analyze_proxy_variables, render_strict_verdict, root_agent
    _ok = True
except Exception as e:
    print(f"WARNING: Agent import failed: {e}")
    _ok = False


@app.get("/health")
async def health():
    return {"status": "healthy", "agent": "strict_auditor_juror", "ready": _ok}


@app.post("/evaluate")
async def evaluate(case_context: Dict[str, Any]):
    """Evaluate case from the Strict Auditor (prosecutor) perspective."""
    if not _ok:
        raise HTTPException(503, "Agent not available")
    try:
        proxy_vars: List[str] = case_context.get("proxy_variables", ["zip_code"])
        red_flags = identify_bias_red_flags(
            disparate_impact_ratio=case_context.get("disparate_impact_ratio", 1.0),
            score_changed_by_proxy=case_context.get("score_changed_by_proxy", False),
            proxy_variables=proxy_vars,
            bias_score=case_context.get("bias_score", 0),
        )
        proxy_analysis = analyze_proxy_variables(
            proxy_variables=proxy_vars,
            disparate_impact_ratio=case_context.get("disparate_impact_ratio", 1.0),
        )
        verdict = render_strict_verdict(red_flags["overall_severity_score"])
        return {
            "juror_id": "strict_auditor_juror",
            "role": "Prosecutor/Strict",
            **verdict,
            "red_flags": red_flags,
            "proxy_analysis": proxy_analysis,
        }
    except Exception as e:
        raise HTTPException(500, str(e))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
