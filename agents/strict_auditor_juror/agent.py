"""
Strict Auditor Juror Agent — ADK 1.0+ pattern
Prosecutor juror: ruthlessly identifies proxy bias and systemic unfairness.
"""
from google.adk.agents import Agent


def identify_bias_red_flags(
    disparate_impact_ratio: float,
    score_changed_by_proxy: bool,
    proxy_variables: list,
    bias_score: float,
) -> dict:
    """
    Identify all bias red flags using strict statistical standards (80% rule, four-fifths test).
    Acts as a prosecutor determining whether the algorithm fails fairness thresholds.

    Args:
        disparate_impact_ratio: DIR from quantitative audit. Below 0.8 = violation.
        score_changed_by_proxy: True if counterfactual flip changed outcome score.
        proxy_variables: List of potential proxy variables in the model (e.g. ['zip_code']).
        bias_score: Overall bias severity (0-100) from the quantitative auditor.

    Returns:
        dict with red_flags list, total_flags, overall_severity_score.
    """
    red_flags = []
    severity = 0

    if disparate_impact_ratio < 0.80:
        red_flags.append({
            "flag": "Disparate Impact Detected",
            "severity": "HIGH",
            "metric": f"DIR={disparate_impact_ratio:.3f} — below 0.8 safe-harbor threshold",
            "legal_standard": "80% / Four-Fifths Rule (EEOC Uniform Guidelines)",
        })
        severity += 40

    if score_changed_by_proxy:
        red_flags.append({
            "flag": "Proxy Bias Confirmed",
            "severity": "HIGH",
            "description": "Counterfactual proxy flip caused measurable score change",
            "implication": "Algorithm encodes hidden discrimination via proxy variable",
        })
        severity += 35

    if proxy_variables:
        red_flags.append({
            "flag": "High-Risk Proxy Variables Present",
            "severity": "HIGH",
            "variables": proxy_variables,
            "concern": "These variables may encode protected characteristics (race, gender, etc.)",
        })
        severity += 25

    if bias_score > 50:
        red_flags.append({
            "flag": "Elevated Composite Bias Score",
            "severity": "MEDIUM" if bias_score <= 70 else "CRITICAL",
            "score": bias_score,
            "threshold_exceeded": True,
        })
        severity += 10

    return {
        "total_red_flags": len(red_flags),
        "red_flags": red_flags,
        "overall_severity_score": min(100, severity),
    }


def analyze_proxy_variables(proxy_variables: list, disparate_impact_ratio: float) -> dict:
    """
    Perform deep-dive analysis of proxy variables to assess discrimination risk.

    Args:
        proxy_variables: List of proxy variables detected in the model.
        disparate_impact_ratio: DIR from quantitative audit.

    Returns:
        dict with per-variable risk assessment and overall proxy risk rating.
    """
    variable_assessments = []
    for var in proxy_variables:
        risk_level = "HIGH" if var in ["zip_code", "name", "postal_code", "neighborhood"] else "MEDIUM"
        variable_assessments.append({
            "variable": var,
            "proxy_risk": risk_level,
            "protected_characteristic_risk": "Race/Ethnicity/SES" if risk_level == "HIGH" else "Unknown",
            "recommendation": f"Remove '{var}' from model or apply counterfactual fairness constraint.",
        })

    overall_risk = "CRITICAL" if disparate_impact_ratio < 0.7 else (
        "HIGH" if disparate_impact_ratio < 0.8 else "MEDIUM"
    )
    return {
        "variable_assessments": variable_assessments,
        "overall_proxy_risk": overall_risk,
        "statistical_overlap_estimate": round(1 - disparate_impact_ratio, 3),
        "prosecutorial_recommendation": "FAIL — Proxy bias confirmed. Model must be retrained." if overall_risk in ("CRITICAL", "HIGH") else "MONITOR — Proxy risk present but manageable.",
    }


def render_strict_verdict(overall_severity_score: float) -> dict:
    """
    Produce the Strict Auditor Juror's formal verdict. Errs on the side of protecting vulnerable populations.

    Args:
        overall_severity_score: Severity score from identify_bias_red_flags (0-100).

    Returns:
        dict with verdict (FAIR | FAIR_WITH_CONCERNS | UNFAIR), confidence, and reasoning.
    """
    if overall_severity_score > 70:
        verdict = "UNFAIR"
        confidence = 0.95
        reasoning = (
            "Multiple high-severity bias indicators confirmed. DIR violates 80% rule, proxy bias is active, "
            "and protected-class variables are embedded via proxies. Algorithm FAILS fairness standards."
        )
    elif overall_severity_score > 45:
        verdict = "FAIR_WITH_CONCERNS"
        confidence = 0.80
        reasoning = (
            "Significant bias concerns identified. Algorithm requires substantial changes — variable removal, "
            "counterfactual fairness constraints, and third-party audit — before any deployment."
        )
    else:
        verdict = "FAIR"
        confidence = 0.70
        reasoning = (
            "Bias indicators present but below critical thresholds. Algorithm meets minimum fairness standards. "
            "Ongoing quarterly monitoring and annual third-party audits strongly recommended."
        )
    return {"verdict": verdict, "confidence": confidence, "reasoning": reasoning}


root_agent = Agent(
    name="strict_auditor_juror",
    model="gemini-2.0-flash",
    description="Prosecutor juror who ruthlessly flags proxy bias, disparate impact, and systemic unfairness.",
    instruction="""You are the Strict Auditor Juror — serving as a relentless prosecutor in the Justice AI audit jury.

Your mandate: find every instance of bias, proxy discrimination, and systemic unfairness. Err on the side of protecting vulnerable populations.

Given the full audit context:

1. Call `identify_bias_red_flags` with disparate_impact_ratio, score_changed_by_proxy, proxy_variables (default ['zip_code']), and bias_score.
2. Call `analyze_proxy_variables` with the proxy_variables list and disparate_impact_ratio.
3. Call `render_strict_verdict` with the overall_severity_score from step 1.

Output a structured JSON verdict:
{
  "juror_id": "strict_auditor_juror",
  "role": "Prosecutor/Strict",
  "verdict": "FAIR | FAIR_WITH_CONCERNS | UNFAIR",
  "confidence": <0-1>,
  "reasoning": "<paragraph>",
  "red_flags": [...],
  "proxy_analysis": {...}
}""",
    tools=[identify_bias_red_flags, analyze_proxy_variables, render_strict_verdict],
)
