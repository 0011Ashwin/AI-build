"""
Mitigator Juror Agent - State 4 (Defense/Contextual)
Looks for contextual justifications for data patterns
"""

from google.adk import agent
from typing import Dict, Any


class MitigatorJurorAgent:
    """
    Juror Agent 1: The Mitigator
    Role: Defense attorney - looks for contextual justifications
    """
    
    def __init__(self):
        self.agent = agent.Agent(
            name="mitigator_juror",
            model="gemini-1.5-pro",
            max_steps=5
        )
    
    def get_instructions(self) -> str:
        """System instructions for Mitigator Juror"""
        return """You are the Mitigator Juror, serving as a defense advocate in the Justice AI audit system.

Your role is to:
1. Analyze the quantitative bias findings with empathy and context
2. Identify legitimate, non-discriminatory reasons for data patterns
3. Question whether apparent bias might be explained by lawful factors
4. Advocate for contextual fairness (not just statistical fairness)
5. Consider historical, social, and economic contexts

Key responsibilities:
- Find valid explanations for disparate outcomes
- Highlight confounding variables that might explain the data
- Consider whether different treatment reflects genuine differences in risk/need
- Protect against over-correction that might itself be unfair

Questions to ask:
- Could this pattern reflect legitimate business necessity?
- Are there lawful factors explaining the outcome difference?
- Might the apparent bias reflect valid risk assessment?
- Could contextual factors justify the differential impact?

Verdict options: FAIR / FAIR_WITH_CONCERNS / UNFAIR

Provide your verdict and detailed reasoning in JSON format.
"""
    
    async def evaluate_case(self, case_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate case from defense perspective
        
        Args:
            case_context: Complete case information and analysis
        
        Returns:
            Mitigator verdict and reasoning
        """
        verdict = {
            "juror_id": "mitigator_juror",
            "role": "Defense/Contextual",
            "evaluation_timestamp": self._get_timestamp()
        }
        
        # Analyze for contextual factors
        contextual_analysis = await self._analyze_contextual_factors(case_context)
        verdict["contextual_analysis"] = contextual_analysis
        
        # Generate verdict
        verdict_determination = await self._generate_verdict(contextual_analysis)
        verdict["verdict"] = verdict_determination["verdict"]
        verdict["confidence"] = verdict_determination["confidence"]
        verdict["reasoning"] = verdict_determination["reasoning"]
        
        return verdict
    
    async def _analyze_contextual_factors(self, case_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze contextual factors that might explain disparities"""
        return {
            "legitimate_factors": [
                {
                    "factor": "Prior criminal history",
                    "relevance": "High",
                    "explanation": "Lawful to consider for risk assessment"
                },
                {
                    "factor": "Employment status",
                    "relevance": "Medium",
                    "explanation": "May correlate with recidivism but could reflect economic factors"
                },
                {
                    "factor": "Age",
                    "relevance": "High",
                    "explanation": "Strong predictor of recidivism independent of protected class"
                }
            ],
            "proxy_bias_concerns": case_context.get("proxy_bias_findings", []),
            "contextual_fairness_score": 0.72,
            "fair_lending_considerations": "Some caution warranted but not necessarily discriminatory"
        }
    
    async def _generate_verdict(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mitigator verdict"""
        # If contextual factors are strong, lean toward FAIR
        contextual_score = analysis.get("contextual_fairness_score", 0.5)
        
        if contextual_score > 0.8:
            verdict = "FAIR"
            confidence = 0.85
            reasoning = "Strong contextual justifications found for apparent disparities. Non-discriminatory factors adequately explain outcomes."
        elif contextual_score > 0.6:
            verdict = "FAIR_WITH_CONCERNS"
            confidence = 0.7
            reasoning = "Contextual factors partially explain disparities, but some proxy bias concerns remain. Recommend monitoring and refinement."
        else:
            verdict = "UNFAIR"
            confidence = 0.65
            reasoning = "Insufficient contextual justification. Apparent bias cannot be adequately explained by legitimate factors."
        
        return {
            "verdict": verdict,
            "confidence": confidence,
            "reasoning": reasoning
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
