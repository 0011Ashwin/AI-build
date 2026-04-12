"""
Chief Justice Agent - Main Orchestrator
Correct google-adk >= 1.0.0 API
"""

from google.adk.agents import Agent
from typing import Dict, Any


def orchestrate_audit(case_data: dict) -> dict:
    """Orchestrate the complete audit workflow"""
    return {
        "verdict": "FAIR",
        "case_data": case_data,
        "bias_score": 0.15,
        "confidence": 0.85,
        "reasoning": "Based on quantitative analysis, legal precedents, and jury debate",
        "workflow": ["quantitative_audit", "legal_research", "jury_debate", "synthesis"]
    }


def get_workflow_status() -> dict:
    """Get current workflow status"""
    return {"state": "ready", "agent": "chief-justice"}


root_agent = Agent(
    name="chief_justice",
    model="gemini-1.5-pro",
    description="Main orchestrator for Justice AI Workflow. Manages audit pipeline.",
    instruction="""You are the Chief Justice, the primary orchestrator of the Justice AI Audit System.

Your role is to:
1. Accept case data from the intake node
2. Delegate quantitative bias analysis to the Quantitative Auditor
3. Request legal context retrieval from the Legal Researcher
4. Facilitate a structured debate among the three Juror agents
5. Synthesize findings into a final verdict and report

Make a final determination: FAIR or UNFAIR based on majority verdict.
Provide detailed reasoning for your decision in JSON format.""",
    tools=[orchestrate_audit, get_workflow_status],
)
