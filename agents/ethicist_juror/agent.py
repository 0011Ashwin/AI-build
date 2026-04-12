"""
Ethicist Juror Agent - State 4 (Ethics/SDG Focus)
Evaluates human impact and SDG alignment
"""

from google.adk import agent
from typing import Dict, Any


class EthicistJurorAgent:
    """
    Juror Agent 3: The Ethicist
    Role: Evaluates human impact and SDG 10/16 alignment
    """
    
    def __init__(self):
        self.agent = agent.Agent(
            name="ethicist_juror",
            model="gemini-1.5-pro",
            max_steps=5
        )
    
    def get_instructions(self) -> str:
        """System instructions for Ethicist Juror"""
        return """You are the Ethicist Juror, serving as the values advocate in the Justice AI audit system.

Your role is to:
1. Evaluate the human impact of algorithmic decisions
2. Assess alignment with UN Sustainable Development Goals (especially SDG 10 & 16)
3. Consider vulnerable populations and marginalized groups
4. Evaluate long-term societal consequences
5. Balance efficiency with human dignity

Key responsibilities:
- Center vulnerable populations in analysis
- Consider systemic and historical injustices
- Evaluate whether the algorithm promotes equality
- Assess impact on institutional trust
- Consider downstream effects on communities

UN Goals Focus:
- SDG 10: Reduce Inequalities (within and among countries)
- SDG 16: Peace, Justice and Strong Institutions

Questions to ask:
- Who is harmed by this decision?
- Does the algorithm promote equality or perpetuate inequality?
- How does this decision affect trust in institutions?
- What are the long-term societal impacts?
- Are vulnerable populations protected?
- Does this align with principles of human dignity?

Verdict options: FAIR / FAIR_WITH_CONCERNS / UNFAIR

Prioritize human dignity and societal welfare over efficiency.
Provide your verdict and detailed reasoning in JSON format.
"""
    
    async def evaluate_case(self, case_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate case from ethical perspective
        
        Args:
            case_context: Complete case information and analysis
        
        Returns:
            Ethicist verdict and reasoning
        """
        verdict = {
            "juror_id": "ethicist_juror",
            "role": "Ethicist/Human Impact",
            "evaluation_timestamp": self._get_timestamp()
        }
        
        # Analyze human impact
        impact_analysis = await self._analyze_human_impact(case_context)
        verdict["human_impact_analysis"] = impact_analysis
        
        # Check SDG alignment
        sdg_alignment = await self._evaluate_sdg_alignment(case_context)
        verdict["sdg_alignment"] = sdg_alignment
        
        # Assess vulnerable population impact
        vulnerable_impact = await self._assess_vulnerable_populations(case_context)
        verdict["vulnerable_population_impact"] = vulnerable_impact
        
        # Generate verdict
        verdict_determination = await self._generate_verdict(
            impact_analysis,
            sdg_alignment,
            vulnerable_impact
        )
        verdict["verdict"] = verdict_determination["verdict"]
        verdict["confidence"] = verdict_determination["confidence"]
        verdict["reasoning"] = verdict_determination["reasoning"]
        
        return verdict
    
    async def _analyze_human_impact(self, case_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze human impact of decision"""
        return {
            "decision_severity": "HIGH",
            "affected_population_size": "Millions",
            "potential_harms": [
                {
                    "harm": "Perpetuation of systemic inequality",
                    "severity": "HIGH",
                    "affected_group": "Minority populations"
                },
                {
                    "harm": "Loss of opportunity",
                    "severity": "HIGH",
                    "affected_group": "Individuals unfairly labeled"
                },
                {
                    "harm": "Erosion of institutional trust",
                    "severity": "MEDIUM",
                    "affected_group": "Community at large"
                }
            ],
            "potential_benefits": [
                {
                    "benefit": "Improved efficiency or accuracy",
                    "significance": "MEDIUM"
                }
            ],
            "overall_human_impact_score": 0.35  # Lower is better
        }
    
    async def _evaluate_sdg_alignment(self, case_context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate alignment with UN Sustainable Development Goals"""
        return {
            "sdg_10_reduce_inequalities": {
                "goal": "Reduce inequality within and among countries",
                "alignment_score": 0.45,
                "finding": "Algorithm may perpetuate inequality - MISALIGNED",
                "reasoning": "Disparate impact and proxy bias inconsistent with SDG 10"
            },
            "sdg_16_peace_justice": {
                "goal": "Promote just, peaceful and inclusive societies",
                "alignment_score": 0.50,
                "finding": "Algorithm undermines institutional fairness - CONCERNING",
                "reasoning": "Lack of transparency and potential bias erodes public trust"
            },
            "overall_sdg_alignment": 0.48,
            "recommendation": "Algorithm requires significant revision to align with SDG values"
        }
    
    async def _assess_vulnerable_populations(self, case_context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess impact on vulnerable populations"""
        return {
            "identified_vulnerable_groups": [
                "Racial minorities",
                "Low-income individuals",
                "Geographic minorities (zip code-based)"
            ],
            "disproportionate_impact": True,
            "protection_level": "INADEQUATE",
            "concerns": [
                {
                    "group": "Racial minorities",
                    "impact": "Potential for discriminatory outcomes",
                    "severity": "HIGH"
                },
                {
                    "group": "Geographic minorities",
                    "impact": "Proxy discrimination via location data",
                    "severity": "HIGH"
                }
            ],
            "marginalized_population_protection_score": 0.35
        }
    
    async def _generate_verdict(
        self,
        impact_analysis: Dict[str, Any],
        sdg_alignment: Dict[str, Any],
        vulnerable_impact: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate ethicist verdict"""
        # Combine scores
        impact_score = impact_analysis.get("overall_human_impact_score", 0)
        sdg_score = sdg_alignment.get("overall_sdg_alignment", 0)
        vulnerable_score = vulnerable_impact.get("marginalized_population_protection_score", 0)
        
        average_score = (impact_score + sdg_score + vulnerable_score) / 3
        
        if average_score < 0.4:  # Lower is worse
            verdict = "UNFAIR"
            confidence = 0.90
            reasoning = "Significant ethical concerns. Algorithm perpetuates inequality, violates SDG principles, and inadequately protects vulnerable populations. Human dignity and fairness values are compromised."
        elif average_score < 0.6:
            verdict = "FAIR_WITH_CONCERNS"
            confidence = 0.75
            reasoning = "Moderate ethical concerns. While some fairness measures are in place, alignment with SDG values and protection of vulnerable populations should be enhanced."
        else:
            verdict = "FAIR"
            confidence = 0.70
            reasoning = "Algorithm demonstrates reasonable ethical alignment. Human impact is mitigated, vulnerable populations are adequately protected, and SDG values are largely respected."
        
        return {
            "verdict": verdict,
            "confidence": confidence,
            "reasoning": reasoning
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
