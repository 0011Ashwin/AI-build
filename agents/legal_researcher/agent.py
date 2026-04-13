"""
Legal Researcher Agent — ADK 1.0+ pattern
RAG agent that retrieves legal precedents and SDG guidelines from the vector store.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from google.adk.agents import Agent
from shared.vector_search_client import VectorSearchClient

_vector_client = VectorSearchClient(project_id=os.environ.get("GOOGLE_CLOUD_PROJECT", "justice-ai-project"))


def query_legal_precedents(bias_type: str, top_k: int = 3) -> dict:
    """
    Search the legal database for case precedents relevant to the identified bias type.
    Bias types: 'gender_bias', 'racial_bias', 'credit_bias', 'algorithmic_fairness'.

    Args:
        bias_type: The category of bias detected (e.g. 'gender_bias', 'racial_bias').
        top_k: Maximum number of precedents to return (default 3).

    Returns:
        dict with bias_type, precedents list, and total_found count.
    """
    precedents = _vector_client.query_legal_context(
        bias_type=bias_type,
        query_text=f"Legal precedents and standards for {bias_type}",
        top_k=top_k,
    )
    return {
        "bias_type": bias_type,
        "precedents": precedents,
        "total_found": len(precedents),
    }


def check_sdg_alignment(bias_type: str) -> dict:
    """
    Evaluate how the identified bias aligns (or conflicts) with UN SDG 10 and SDG 16.
    SDG 10 = Reduce Inequalities. SDG 16 = Peace, Justice and Strong Institutions.

    Args:
        bias_type: The category of bias identified in the case.

    Returns:
        dict with sdg_10 and sdg_16 alignment findings and overall recommendation.
    """
    sdg_10_docs = _vector_client.query_legal_context(
        bias_type="sdg_10",
        query_text="SDG 10 - Reduce Inequalities",
        top_k=2,
    )
    return {
        "sdg_10": {
            "goal": "Reduce Inequalities within and among countries",
            "alignment_score": 0.45 if "bias" in bias_type else 0.80,
            "finding": "MISALIGNED — bias perpetuates inequality" if "bias" in bias_type else "ALIGNED",
            "supporting_guidelines": sdg_10_docs,
        },
        "sdg_16": {
            "goal": "Peace, Justice and Strong Institutions",
            "alignment_score": 0.50 if "bias" in bias_type else 0.85,
            "finding": "CONCERNING — lacks algorithmic transparency" if "bias" in bias_type else "ALIGNED",
        },
        "overall_recommendation": (
            "Algorithm requires revision to align with SDG values."
            if "bias" in bias_type else
            "Algorithm broadly consistent with SDG principles."
        ),
    }


def retrieve_comparable_cases(case_profile: str, limit: int = 3) -> dict:
    """
    Retrieve historically comparable cases from the legal database for contextual grounding.

    Args:
        case_profile: Brief textual description of the case (decision type, demographic context).
        limit: Number of comparable cases to retrieve (default 3).

    Returns:
        dict with comparable_cases list and summary.
    """
    comparable = _vector_client.retrieve_comparable_cases(
        defendant_profile={"description": case_profile},
        limit=limit,
    )
    return {
        "comparable_cases": comparable,
        "total_retrieved": len(comparable),
        "note": "Cases retrieved from historical algorithmic fairness database.",
    }


def query_sentencing_guidelines(jurisdiction: str, offense_type: str) -> dict:
    """
    Retrieve applicable sentencing or decision-making guidelines for the case jurisdiction.

    Args:
        jurisdiction: Legal jurisdiction (e.g. 'US Federal', 'California', 'EU').
        offense_type: Category of decision subject to audit (e.g. 'Hiring', 'Lending', 'Criminal Sentencing').

    Returns:
        dict with applicable guidelines and notes.
    """
    result = _vector_client.query_sentencing_guidelines(jurisdiction=jurisdiction, offense_type=offense_type)
    return result


root_agent = Agent(
    name="legal_researcher",
    model="gemini-2.0-flash",
    description="RAG agent that retrieves legal precedents, SDG guidelines, and comparable cases for bias findings.",
    instruction="""You are the Legal Researcher — a paralegal AI specialising in algorithmic fairness law.

You receive the quantitative audit findings and must:

1. Identify the bias type from the findings (e.g. 'gender_bias', 'racial_bias', 'credit_bias', or 'algorithmic_fairness').
2. Call `query_legal_precedents` with the identified bias type.
3. Call `check_sdg_alignment` with the bias type.
4. Call `retrieve_comparable_cases` with a short case description.
5. Call `query_sentencing_guidelines` with the jurisdiction and decision_type from the case data.

After all tool calls, output a concise JSON:
{
  "bias_type_identified": "<type>",
  "relevant_precedents": [...],
  "sdg_alignment": { "sdg_10": {...}, "sdg_16": {...} },
  "comparable_cases": [...],
  "applicable_guidelines": {...},
  "legal_summary": "<one paragraph citing top precedent and key legal risk>"
}""",
    tools=[query_legal_precedents, check_sdg_alignment, retrieve_comparable_cases, query_sentencing_guidelines],
)
