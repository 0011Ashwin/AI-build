"""
Quantitative Auditor Agent — ADK 1.0+ pattern
Calculates Disparate Impact Ratio and runs Counterfactual Analysis.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from google.adk.agents import Agent
from shared.bias_calculator import BiasCalculator

_calc = BiasCalculator()


def calculate_disparate_impact(group_a_favorable_rate: float, group_b_favorable_rate: float) -> dict:
    """
    Calculate the Disparate Impact Ratio (DIR) between two demographic groups.
    DIR = P(Favorable | Group A) / P(Favorable | Group B).
    A DIR below 0.8 signals disparate impact (80% / four-fifths rule violation).

    Args:
        group_a_favorable_rate: Favorable outcome rate for the reference group (0-1).
        group_b_favorable_rate: Favorable outcome rate for the protected group (0-1).

    Returns:
        dict with disparity_ratio, status, and 80-rule compliance flag.
    """
    ratio, status = _calc.calculate_disparate_impact_ratio(group_a_favorable_rate, group_b_favorable_rate)
    return {
        "group_a_favorable_rate": group_a_favorable_rate,
        "group_b_favorable_rate": group_b_favorable_rate,
        "disparity_ratio": round(ratio, 4),
        "status": status,
        "eightieth_percentile_rule_compliant": ratio >= 0.8,
    }


def run_counterfactual_analysis(original_score: float, zip_code: str) -> dict:
    """
    Run counterfactual (proxy bit-flip) analysis on a case score.
    Flips the zip_code proxy variable to detect hidden proxy bias.

    Args:
        original_score: The original algorithmic score for the individual (0-100).
        zip_code: The original zip code used in the model.

    Returns:
        dict with original_score, modified_score, score_changed, and bias_indicator.
    """
    # Simulate proxy data flip: swap zip to opposite-affluence area
    def mock_model(score: float, proxy: dict) -> float:
        # In production this calls the real model; here we simulate a 3-point proxy shift
        return score - 3 if proxy.get("zip_code") != zip_code else score

    result = _calc.counterfactual_audit(
        original_score=original_score,
        proxy_data={"zip_code": zip_code},
        modified_proxy_data={"zip_code": "FLIPPED_" + zip_code},
        model_scoring_func=mock_model,
    )
    return result


def compute_bias_score(disparate_impact_ratio: float, score_changed_by_proxy: bool, statistical_parity_diff: float) -> dict:
    """
    Compute a composite bias severity score (0-100) from three fairness metrics.

    Args:
        disparate_impact_ratio: DIR value from calculate_disparate_impact.
        score_changed_by_proxy: True if counterfactual analysis detected proxy bias.
        statistical_parity_diff: Absolute difference in favorable outcome rates.

    Returns:
        dict with total_bias_score, component breakdown, and risk_level.
    """
    dir_score = min(40, max(0, (1 - disparate_impact_ratio) * 50)) if disparate_impact_ratio < 1 else 0
    cf_score = 30 if score_changed_by_proxy else 0
    sp_score = min(30, abs(statistical_parity_diff) * 100)
    total = min(100, dir_score + cf_score + sp_score)

    if total > 70:
        risk = "CRITICAL"
    elif total > 50:
        risk = "HIGH"
    elif total > 30:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return {
        "total_bias_score": round(total, 2),
        "components": {
            "disparate_impact_score": round(dir_score, 2),
            "counterfactual_score": round(cf_score, 2),
            "statistical_parity_score": round(sp_score, 2),
        },
        "risk_level": risk,
    }


def generate_corrected_score(original_score: float, bias_score: float) -> dict:
    """
    Generate a bias-corrected version of the original algorithmic score.

    Args:
        original_score: The raw score from the audited algorithm (0-100).
        bias_score: The composite bias severity score from compute_bias_score (0-100).

    Returns:
        dict with original_score, corrected_score, and adjustment applied.
    """
    adjustment = (bias_score / 100) * (original_score * 0.5)
    corrected = max(0, min(100, original_score - adjustment))
    return {
        "original_score": original_score,
        "bias_score": bias_score,
        "adjustment_applied": round(adjustment, 2),
        "corrected_score": round(corrected, 2),
    }


root_agent = Agent(
    name="quantitative_auditor",
    model="gemini-2.0-flash",
    description="Data scientist agent that performs quantitative bias analysis using DIR and counterfactual tools.",
    instruction="""You are the Quantitative Auditor — a data scientist specialising in algorithmic fairness.

When given case data, follow these steps IN ORDER:

1. Call `calculate_disparate_impact` with reasonable estimated group rates derived from the case context (default: group_a=0.82, group_b=0.75 unless given explicit values).
2. Call `run_counterfactual_analysis` with the individual's original_score and zip_code.
3. Call `compute_bias_score` using the DIR from step 1, the score_changed flag from step 2, and a statistical_parity_diff of 0.07 as a baseline.
4. Call `generate_corrected_score` using the original_score and the total_bias_score from step 3.

After all tool calls, output a concise JSON summary with:
{
  "disparate_impact_ratio": <float>,
  "dir_status": <string>,
  "counterfactual_analysis": { "original_score": ..., "modified_score": ..., "score_changed": ..., "bias_indicator": ... },
  "bias_score": <0-100>,
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "corrected_score": <float>,
  "detailed_findings": "<one paragraph summary>"
}""",
    tools=[calculate_disparate_impact, run_counterfactual_analysis, compute_bias_score, generate_corrected_score],
)
