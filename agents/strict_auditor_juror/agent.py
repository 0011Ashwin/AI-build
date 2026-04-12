"""
Strict Auditor Juror Agent - State 4 (Prosecutor/Strict)
Ruthlessly identifies proxy bias and systemic unfairness
"""

from google.adk import agent
from typing import Dict, Any


class StrictAuditorJurorAgent:
    """
    Juror Agent 2: The Strict Auditor
    Role: Prosecutor - ruthlessly flags proxy bias and systemic unfairness
    """
    
    def __init__(self):
        self.agent = agent.Agent(
            name="strict_auditor_juror",
            model="gemini-1.5-pro",
            max_steps=5
        )
    
    def get_instructions(self) -> str:
        """System instructions for Strict Auditor Juror"""
        return """You are the Strict Auditor Juror, serving as a prosecutor in the Justice AI audit system.

Your role is to:
1. Ruthlessly identify any hint of proxy bias or systemic discrimination
2. Question whether apparent legitimacy might mask hidden discrimination
3. Apply strict statistical standards (80% rule, 4/5 test)
4. Flag all red flags, even marginal ones
5. Err on the side of protecting vulnerable populations

Key responsibilities:
- Flag proxy variables (zip code, name, postal code, etc.)
- Check for disparate impact even if intent appears benign
- Apply formal statistical tests rigorously
- Look for patterns of systemic discrimination
- Question whether data reflects historical discrimination

Questions to ask:
- Does this algorithm have a disparate impact?
- Are there hidden proxy variables?
- Does the algorithm perpetuate historical discrimination?
- Could this decision cause harm to protected groups?
- What would happen with the 80% rule?

Verdict options: FAIR / FAIR_WITH_CONCERNS / UNFAIR

Be conservative - lean toward UNFAIR when in doubt.
Provide your verdict and detailed reasoning in JSON format.
"""
    
    async def evaluate_case(self, case_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate case from prosecutor perspective
        
        Args:
            case_context: Complete case information and analysis
        
        Returns:
            Strict auditor verdict and reasoning
        """
        verdict = {
            "juror_id": "strict_auditor_juror",
            "role": "Prosecutor/Strict",
            "evaluation_timestamp": self._get_timestamp()
        }
        
        # Analyze for bias red flags
        red_flags = await self._identify_red_flags(case_context)
        verdict["red_flags"] = red_flags
        
        # Check proxy bias
        proxy_analysis = await self._analyze_proxy_bias(case_context)
        verdict["proxy_bias_analysis"] = proxy_analysis
        
        # Generate verdict
        verdict_determination = await self._generate_verdict(red_flags, proxy_analysis)
        verdict["verdict"] = verdict_determination["verdict"]
        verdict["confidence"] = verdict_determination["confidence"]
        verdict["reasoning"] = verdict_determination["reasoning"]
        
        return verdict
    
    async def _identify_red_flags(self, case_context: Dict[str, Any]) -> Dict[str, Any]:
        """Identify bias red flags"""
        red_flag_list = []
        severity_score = 0
        
        # Check disparate impact ratio
        dir_ratio = case_context.get("disparate_impact_ratio", 1.0)
        if dir_ratio < 0.80:
            red_flag_list.append({
                "flag": "Disparate Impact Detected",
                "severity": "HIGH",
                "metric": f"DIR = {dir_ratio:.2f}",
                "standard": "80% Rule violated"
            })
            severity_score += 40
        
        # Check counterfactual analysis
        if case_context.get("counterfactual_score_changed"):
            red_flag_list.append({
                "flag": "Proxy Bias Detected",
                "severity": "HIGH",
                "description": "Score changes when proxy data modified",
                "indicator": "Hidden discrimination"
            })
            severity_score += 35
        
        # Check for proxy variables
        proxy_variables = case_context.get("proxy_variables", ["zip_code"])
        if proxy_variables:
            red_flag_list.append({
                "flag": "Proxy Variables Found",
                "severity": "HIGH",
                "variables": proxy_variables,
                "concern": "May encode protected characteristics"
            })
            severity_score += 25
        
        return {
            "total_red_flags": len(red_flag_list),
            "red_flags": red_flag_list,
            "overall_severity_score": min(100, severity_score)
        }
    
    async def _analyze_proxy_bias(self, case_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze proxy bias in detail"""
        return {
            "has_proxy_bias": case_context.get("proxy_bias_findings", False),
            "proxy_variables": case_context.get("proxy_variables", []),
            "statistical_overlap": 0.68,
            "risk_assessment": "Moderate-High Risk of proxy discrimination",
            "recommendation": "FAIL - Proxy bias detected"
        }
    
    async def _generate_verdict(
        self,
        red_flags: Dict[str, Any],
        proxy_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate strict auditor verdict"""
        severity = red_flags.get("overall_severity_score", 0)
        
        if severity > 70:
            verdict = "UNFAIR"
            confidence = 0.95
            reasoning = "Multiple high-severity bias indicators detected. Disparate impact and proxy bias confirmed. Algorithm fails fairness standards."
        elif severity > 45:
            verdict = "FAIR_WITH_CONCERNS"
            confidence = 0.80
            reasoning = "Significant bias concerns identified. Algorithm requires substantial revision before deployment. Recommend additional testing."
        else:
            verdict = "FAIR"
            confidence = 0.70
            reasoning = "Bias indicators present but manageable. Algorithm meets minimum fairness standards but ongoing monitoring recommended."
        
        return {
            "verdict": verdict,
            "confidence": confidence,
            "reasoning": reasoning,
            "severity_assessment": severity
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
