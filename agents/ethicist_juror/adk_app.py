"""
Ethicist Juror — Cloud Run HTTP wrapper.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List

app = FastAPI(title="Ethicist Juror Agent", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

try:
    from agent import evaluate_human_impact, assess_sdg_alignment, assess_vulnerable_populations, render_ethicist_verdict, root_agent
    _ok = True
except Exception as e:
    print(f"WARNING: Agent import failed: {e}")
    _ok = False


@app.get("/health")
async def health():
    return {"status": "healthy", "agent": "ethicist_juror", "ready": _ok}


@app.post("/evaluate")
async def evaluate(case_context: Dict[str, Any]):
    """Evaluate case from the Ethicist (SDG/human-impact) perspective."""
    if not _ok:
        raise HTTPException(503, "Agent not available")
    try:
        proxy_vars: List[str] = case_context.get("proxy_variables", ["zip_code"])
        human = evaluate_human_impact(
            bias_score=case_context.get("bias_score", 0),
            decision_type=case_context.get("decision_type", "General"),
            risk_level=case_context.get("risk_level", "MEDIUM"),
        )
        sdg = assess_sdg_alignment(
            bias_score=case_context.get("bias_score", 0),
            decision_type=case_context.get("decision_type", "General"),
        )
        vulnerable = assess_vulnerable_populations(
            bias_score=case_context.get("bias_score", 0),
            proxy_variables=proxy_vars,
            decision_type=case_context.get("decision_type", "General"),
        )
        verdict = render_ethicist_verdict(
            human_impact_score=human["overall_human_impact_score"],
            sdg_alignment_score=sdg["overall_sdg_alignment"],
            marginalized_protection_score=vulnerable["marginalized_protection_score"],
        )
        return {
            "juror_id": "ethicist_juror",
            "role": "Ethicist/SDG-Focused",
            **verdict,
            "sdg_alignment": sdg,
            "human_impact": human,
            "vulnerable_population_impact": vulnerable,
        }
    except Exception as e:
        raise HTTPException(500, str(e))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
