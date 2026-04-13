"""
Ethicist Juror Agent — ADK 1.0+ pattern
SDG-focused juror: evaluates human impact, equity, and alignment with UN goals.
"""
from google.adk.agents import Agent


def evaluate_human_impact(
    bias_score: float,
    decision_type: str,
    risk_level: str,
) -> dict:
    """
    Evaluate the human and societal impact of the algorithmic decision being audited.
    Considers harm severity, affected population size, and institutional trust effects.

    Args:
        bias_score: Composite bias severity score from the quantitative auditor (0-100).
        decision_type: Type of decision being audited (e.g. 'Hiring', 'Lending', 'Sentencing').
        risk_level: Risk tier from quantitative auditor ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL').

    Returns:
        dict with potential_harms, overall_human_impact_score, and decision_severity.
    """
    severity_map = {"LOW": "LOW", "MEDIUM": "MEDIUM", "HIGH": "HIGH", "CRITICAL": "CRITICAL"}
    decision_severity = severity_map.get(risk_level, "MEDIUM")

    potential_harms = [
        {
            "harm": "Perpetuation of systemic inequality",
            "severity": "HIGH" if bias_score > 40 else "LOW",
            "affected_group": "Minority and low-income populations",
        },
        {
            "harm": f"Unjust denial of {decision_type} opportunity",
            "severity": "HIGH" if decision_type in ("Hiring", "Lending", "Sentencing") else "MEDIUM",
            "affected_group": "Individuals flagged by biased algorithm",
        },
        {
            "harm": "Erosion of public trust in AI systems",
            "severity": "MEDIUM",
            "affected_group": "Community at large",
        },
    ]

    # Lower score = worse human outcome (higher impact)
    impact_score = max(0.0, round(1.0 - (bias_score / 100), 2))

    return {
        "decision_severity": decision_severity,
        "potential_harms": potential_harms,
        "potential_benefits": [{"benefit": "Efficiency / processing speed", "significance": "LOW"}],
        "overall_human_impact_score": impact_score,
        "note": "Impact score of 0 = worst outcome, 1 = best outcome.",
    }


def assess_sdg_alignment(bias_score: float, decision_type: str) -> dict:
    """
    Assess alignment of the audited algorithm with UN Sustainable Development Goals 10 and 16.
    SDG 10 = Reduce Inequalities. SDG 16 = Peace, Justice and Strong Institutions.

    Args:
        bias_score: Bias severity score (0-100). Higher scores indicate worse SDG alignment.
        decision_type: Type of algorithmic decision being audited.

    Returns:
        dict with SDG 10 and SDG 16 alignment scores, findings, and overall recommendation.
    """
    sdg10_alignment = round(max(0.1, 1.0 - (bias_score / 120)), 2)
    sdg16_alignment = round(max(0.2, 1.0 - (bias_score / 150)), 2)

    return {
        "sdg_10_reduce_inequalities": {
            "goal": "Reduce inequality within and among countries",
            "alignment_score": sdg10_alignment,
            "finding": "MISALIGNED — algorithm perpetuates inequality" if sdg10_alignment < 0.5 else "PARTIALLY ALIGNED",
            "reasoning": f"{decision_type} algorithm with bias score {bias_score} conflicts with SDG 10 equitable access principle.",
        },
        "sdg_16_peace_justice": {
            "goal": "Promote just, peaceful and inclusive societies",
            "alignment_score": sdg16_alignment,
            "finding": "CONCERNING — algorithmic opacity undermines institutional trust" if sdg16_alignment < 0.6 else "ACCEPTABLE",
            "reasoning": "Lack of explainability and presence of proxy bias erodes trust in automated decision-making.",
        },
        "overall_sdg_alignment": round((sdg10_alignment + sdg16_alignment) / 2, 2),
        "recommendation": (
            "Substantial revision needed to achieve SDG compliance."
            if bias_score > 40 else
            "Minor adjustments required; algorithm broadly consistent with SDG principles."
        ),
    }


def assess_vulnerable_populations(
    bias_score: float,
    proxy_variables: list,
    decision_type: str,
) -> dict:
    """
    Assess the disproportionate impact of the algorithm on vulnerable and marginalised groups.

    Args:
        bias_score: Bias severity score from quantitative auditor (0-100).
        proxy_variables: List of proxy variables present in the model.
        decision_type: Type of decision being audited.

    Returns:
        dict with identified vulnerable groups, disproportionate_impact flag, and protection assessment.
    """
    at_risk_groups = ["Racial minorities", "Low-income individuals"]
    if any(v in ["zip_code", "postal_code", "neighborhood"] for v in proxy_variables):
        at_risk_groups.append("Geographic minorities (location-based discrimination)")

    disproportionate = bias_score > 30

    protection_level = "INADEQUATE" if bias_score > 50 else ("PARTIAL" if bias_score > 25 else "ADEQUATE")

    return {
        "identified_vulnerable_groups": at_risk_groups,
        "disproportionate_impact": disproportionate,
        "protection_level": protection_level,
        "concerns": [
            {"group": g, "severity": "HIGH" if bias_score > 50 else "MEDIUM",
             "impact": f"Potential for discriminatory {decision_type} outcomes"}
            for g in at_risk_groups
        ],
        "marginalized_protection_score": round(max(0.0, 1.0 - (bias_score / 100)), 2),
    }


def render_ethicist_verdict(
    human_impact_score: float,
    sdg_alignment_score: float,
    marginalized_protection_score: float,
) -> dict:
    """
    Produce the Ethicist Juror's formal verdict. Prioritises human dignity over efficiency.

    Args:
        human_impact_score: From evaluate_human_impact (0-1, higher = better).
        sdg_alignment_score: Overall SDG alignment from assess_sdg_alignment (0-1).
        marginalized_protection_score: From assess_vulnerable_populations (0-1).

    Returns:
        dict with verdict, confidence, and ethical reasoning.
    """
    avg = (human_impact_score + sdg_alignment_score + marginalized_protection_score) / 3

    if avg < 0.4:
        verdict = "UNFAIR"
        confidence = 0.90
        reasoning = (
            "Significant ethical failures detected. Algorithm perpetuates inequality, violates SDG 10/16 principles, "
            "and inadequately protects vulnerable populations. Human dignity is compromised. Immediate suspension recommended."
        )
    elif avg < 0.65:
        verdict = "FAIR_WITH_CONCERNS"
        confidence = 0.75
        reasoning = (
            "Moderate ethical concerns. Fairness safeguards exist but SDG alignment and marginalized population "
            "protections need significant enhancement before broader deployment."
        )
    else:
        verdict = "FAIR"
        confidence = 0.70
        reasoning = (
            "Algorithm demonstrates reasonable ethical alignment. Human impact is mitigated, vulnerable populations "
            "are adequately protected, and SDG values are largely respected."
        )
    return {"verdict": verdict, "confidence": confidence, "reasoning": reasoning}


root_agent = Agent(
    name="ethicist_juror",
    model="gemini-2.0-flash",
    description="Ethics and SDG-focused juror who evaluates human dignity, inequality, and societal impact.",
    instruction="""You are the Ethicist Juror — the values advocate in the Justice AI audit jury.

Your focus: human dignity, SDG alignment, and protection of marginalised populations above all else.

Given the full audit context:

1. Call `evaluate_human_impact` with bias_score, decision_type, and risk_level.
2. Call `assess_sdg_alignment` with bias_score and decision_type.
3. Call `assess_vulnerable_populations` with bias_score, proxy_variables (default ['zip_code']), and decision_type.
4. Call `render_ethicist_verdict` with the three scores from steps 1, 2, and 3.

Output a structured JSON verdict:
{
  "juror_id": "ethicist_juror",
  "role": "Ethicist/SDG-Focused",
  "verdict": "FAIR | FAIR_WITH_CONCERNS | UNFAIR",
  "confidence": <0-1>,
  "reasoning": "<paragraph>",
  "sdg_alignment": { "sdg_10": {...}, "sdg_16": {...}, "overall": <score> },
  "vulnerable_population_impact": {...}
}""",
    tools=[evaluate_human_impact, assess_sdg_alignment, assess_vulnerable_populations, render_ethicist_verdict],
)
