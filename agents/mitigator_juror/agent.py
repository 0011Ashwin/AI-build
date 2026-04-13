"""
Mitigator Juror Agent — ADK 1.0+ pattern
Defense attorney juror: finds contextual justifications for data patterns.
"""
from google.adk.agents import Agent


def evaluate_contextual_fairness(
    bias_score: float,
    disparate_impact_ratio: float,
    score_changed_by_proxy: bool,
    decision_type: str,
) -> dict:
    """
    Evaluate whether apparent bias can be explained by legitimate, non-discriminatory contextual factors.
    Acts as a defense attorney looking for valid business-necessity justifications.

    Args:
        bias_score: Overall bias severity score from quantitative auditor (0-100).
        disparate_impact_ratio: DIR value from quantitative audit (0-2+).
        score_changed_by_proxy: Whether counterfactual proxy flip changed the outcome score.
        decision_type: Type of decision being audited (e.g. 'Hiring', 'Lending', 'Sentencing').

    Returns:
        dict with legitimate_factors, contextual_fairness_score, and mitigation_recommendations.
    """
    legitimate_factors = [
        {"factor": "Prior relevant history", "relevance": "High",
         "explanation": "Lawful to consider objective risk-correlated history"},
        {"factor": "Employment / financial stability indicators", "relevance": "Medium",
         "explanation": "May correlate with outcomes but requires careful scrutiny"},
        {"factor": "Age", "relevance": "High",
         "explanation": "Strong validated predictor independent of protected class"},
    ]

    # Contextual score: higher = more defensible
    base_score = 1.0
    if bias_score > 70:
        base_score -= 0.5
    elif bias_score > 40:
        base_score -= 0.3
    if score_changed_by_proxy:
        base_score -= 0.2
    if disparate_impact_ratio < 0.8:
        base_score -= 0.15
    contextual_fairness_score = max(0.0, round(base_score, 2))

    recommendations = []
    if score_changed_by_proxy:
        recommendations.append("Remove or re-weight the zip code proxy variable.")
    if disparate_impact_ratio < 0.8:
        recommendations.append(f"Adjust model to bring DIR above 0.8 threshold (currently {disparate_impact_ratio:.2f}).")
    recommendations.append(f"Conduct periodic fairness monitoring for {decision_type} pipeline.")

    return {
        "legitimate_factors": legitimate_factors,
        "contextual_fairness_score": contextual_fairness_score,
        "mitigation_recommendations": recommendations,
        "fair_lending_note": "Some caution warranted; assess whether disparities reflect genuine risk or proxy discrimination.",
    }


def render_mitigator_verdict(contextual_fairness_score: float) -> dict:
    """
    Produce the Mitigator Juror's formal verdict based on contextual fairness score.

    Args:
        contextual_fairness_score: Score from evaluate_contextual_fairness (0.0-1.0).

    Returns:
        dict with verdict (FAIR | FAIR_WITH_CONCERNS | UNFAIR), confidence, and reasoning.
    """
    if contextual_fairness_score > 0.8:
        verdict = "FAIR"
        confidence = 0.85
        reasoning = (
            "Strong contextual justifications found. Non-discriminatory factors adequately explain outcome patterns. "
            "No remediation required beyond routine monitoring."
        )
    elif contextual_fairness_score > 0.55:
        verdict = "FAIR_WITH_CONCERNS"
        confidence = 0.70
        reasoning = (
            "Contextual factors partially explain disparities, but proxy bias concerns remain unresolved. "
            "Recommend variable audit, bias mitigation retraining, and quarterly reporting."
        )
    else:
        verdict = "UNFAIR"
        confidence = 0.65
        reasoning = (
            "Insufficient contextual justification. Apparent bias cannot be adequately explained by legitimate factors. "
            "Algorithm must be suspended pending comprehensive fairness review."
        )
    return {"verdict": verdict, "confidence": confidence, "reasoning": reasoning}


root_agent = Agent(
    name="mitigator_juror",
    model="gemini-2.0-flash",
    description="Defense-attorney juror who searches for legitimate contextual justifications for observed bias patterns.",
    instruction="""You are the Mitigator Juror — serving as a defense advocate in the Justice AI audit jury.

Your role: find valid, non-discriminatory reasons that might explain apparent bias before condemning the algorithm.

Given the full audit context (bias_score, disparate_impact_ratio, score_changed_by_proxy, decision_type):

1. Call `evaluate_contextual_fairness` with those four values.
2. Call `render_mitigator_verdict` with the contextual_fairness_score from step 1.

Output a structured JSON verdict:
{
  "juror_id": "mitigator_juror",
  "role": "Defense/Contextual",
  "verdict": "FAIR | FAIR_WITH_CONCERNS | UNFAIR",
  "confidence": <0-1>,
  "reasoning": "<paragraph>",
  "contextual_analysis": { "legitimate_factors": [...], "recommendations": [...] }
}""",
    tools=[evaluate_contextual_fairness, render_mitigator_verdict],
)
