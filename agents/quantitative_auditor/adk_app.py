"""
Quantitative Auditor — Cloud Run HTTP wrapper.
Exposes the agent's bias calculation tools as REST endpoints.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

app = FastAPI(title="Quantitative Auditor Agent", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

try:
    from agent import (
        calculate_disparate_impact,
        run_counterfactual_analysis,
        compute_bias_score,
        generate_corrected_score,
        root_agent,
    )
    _ok = True
except Exception as e:
    print(f"WARNING: Agent import failed: {e}")
    _ok = False


@app.get("/health")
async def health():
    return {"status": "healthy", "agent": "quantitative_auditor", "ready": _ok}


@app.post("/analyze")
async def analyze(case_data: Dict[str, Any]):
    """Run full quantitative bias analysis on a case."""
    if not _ok:
        raise HTTPException(503, "Agent not available")
    try:
        dir_result = calculate_disparate_impact(
            case_data.get("group_a_rate", 0.82),
            case_data.get("group_b_rate", 0.75),
        )
        cf_result = run_counterfactual_analysis(
            case_data.get("original_score", 75.0),
            case_data.get("zip_code", "00000"),
        )
        bias_result = compute_bias_score(
            dir_result["disparity_ratio"],
            cf_result["score_changed"],
            0.07,
        )
        corrected = generate_corrected_score(
            case_data.get("original_score", 75.0),
            bias_result["total_bias_score"],
        )
        return {
            "disparate_impact": dir_result,
            "counterfactual": cf_result,
            "bias_score": bias_result,
            "corrected_score": corrected,
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/tools/calculate-dir")
async def calculate_dir(data: Dict[str, Any]):
    if not _ok:
        raise HTTPException(503, "Agent not available")
    return calculate_disparate_impact(data.get("group_a_rate", 0.82), data.get("group_b_rate", 0.75))


@app.post("/tools/counterfactual")
async def counterfactual(data: Dict[str, Any]):
    if not _ok:
        raise HTTPException(503, "Agent not available")
    return run_counterfactual_analysis(data.get("original_score", 75.0), data.get("zip_code", "00000"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
