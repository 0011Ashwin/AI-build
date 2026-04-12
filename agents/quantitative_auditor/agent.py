"""
Quantitative Auditor Agent - State 1 & 2
Performs bias calculations and counterfactual analysis
"""

from google.adk import agent
from typing import Dict, Any
import sys
sys.path.append('../..')
from shared.bias_calculator import BiasCalculator


class QuantitativeAuditorAgent:
    """
    State 1 & 2 Handler: Data Intake + Audit Chamber
    Performs quantitative bias analysis
    """
    
    def __init__(self):
        self.agent = agent.Agent(
            name="quantitative_auditor",
            model="gemini-1.5-pro",
            max_steps=5
        )
        self.bias_calculator = BiasCalculator()
    
    def get_instructions(self) -> str:
        """System instructions for Quantitative Auditor"""
        return """You are the Quantitative Auditor, a data scientist specializing in algorithmic fairness.

Your responsibilities:
1. Analyze intake data (name, age, priors, zip code, etc.)
2. Calculate Disparate Impact Ratio (DIR) between demographic groups
3. Perform counterfactual analysis (e.g., "What if we changed the zip code?")
4. Generate a comprehensive bias score (0-100)
5. Identify risk level: LOW, MEDIUM, HIGH, or CRITICAL

You must:
- Use rigorous statistical methods
- Flag proxy bias (when proxy data like zip code causes score changes)
- Calculate statistical parity differences
- Provide technical documentation for all metrics

Output format (JSON):
{
    "disparate_impact_ratio": 0.95,
    "dir_status": "FAIR - Within Safe Harbor",
    "counterfactual_analysis": {
        "original_score": 75,
        "modified_score": 72,
        "score_changed": true,
        "bias_detected": "Proxy Bias"
    },
    "bias_score": 45,
    "risk_level": "MEDIUM",
    "detailed_findings": "..."
}
"""
    
    async def analyze_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze case for bias
        
        Args:
            case_data: Case information including demographics and data
        
        Returns:
            Comprehensive bias analysis
        """
        analysis = {
            "intake_data": case_data,
            "analysis_timestamp": self._get_timestamp(),
            "analyses": {}
        }
        
        # Perform Disparate Impact Analysis
        dir_analysis = await self._calculate_disparate_impact(case_data)
        analysis["analyses"]["disparate_impact"] = dir_analysis
        
        # Perform Counterfactual Analysis
        cf_analysis = await self._perform_counterfactual_analysis(case_data)
        analysis["analyses"]["counterfactual"] = cf_analysis
        
        # Calculate Overall Bias Score
        bias_score = await self._calculate_bias_score(dir_analysis, cf_analysis)
        analysis["bias_score"] = bias_score
        analysis["risk_level"] = self._determine_risk_level(bias_score)
        
        # Generate corrected score
        analysis["corrected_score"] = await self._generate_corrected_score(
            case_data.get("original_score", 0),
            bias_score
        )
        
        return analysis
    
    async def _calculate_disparate_impact(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Disparate Impact Ratio"""
        # Simulate group statistics
        group_a_favorable_rate = 0.82  # Assuming high favorable rate
        group_b_favorable_rate = 0.75  # Assuming lower rate
        
        dir_ratio, status = self.bias_calculator.calculate_disparate_impact_ratio(
            group_a_favorable_rate,
            group_b_favorable_rate
        )
        
        return {
            "group_a_favorable_rate": group_a_favorable_rate,
            "group_b_favorable_rate": group_b_favorable_rate,
            "disparity_ratio": dir_ratio,
            "status": status,
            "eightieth_percentile_rule_compliant": dir_ratio >= 0.8
        }
    
    async def _perform_counterfactual_analysis(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform counterfactual analysis with proxy data flipping"""
        original_score = case_data.get("original_score", 75)
        proxy_data = {"zip_code": case_data.get("zip_code", "12345")}
        
        # Simulate proxy data flip
        modified_proxy_data = {"zip_code": "54321"}
        
        # Simulate model response
        def mock_model_scoring(score, proxy):
            # In reality, this would call the actual model
            return score - 3 if proxy["zip_code"] == "54321" else score
        
        result = self.bias_calculator.counterfactual_audit(
            original_score,
            proxy_data,
            modified_proxy_data,
            mock_model_scoring
        )
        
        return result
    
    async def _calculate_bias_score(
        self,
        dir_analysis: Dict[str, Any],
        cf_analysis: Dict[str, Any]
    ) -> float:
        """Calculate comprehensive bias score"""
        # DIR component
        dir_ratio = dir_analysis.get("disparity_ratio", 1.0)
        dir_score = min(40, max(0, (1 - dir_ratio) * 50)) if dir_ratio < 1 else 0
        
        # Counterfactual component
        cf_score = 30 if cf_analysis.get("score_changed") else 0
        
        # Statistical parity component (simulated)
        sp_score = 15
        
        total = min(100, dir_score + cf_score + sp_score)
        return total
    
    async def _generate_corrected_score(
        self,
        original_score: float,
        bias_severity: float
    ) -> float:
        """Generate bias-corrected score"""
        adjustment = (bias_severity / 100) * (original_score * 0.5)
        corrected = original_score - adjustment
        return max(0, min(100, corrected))
    
    def _determine_risk_level(self, bias_score: float) -> str:
        """Determine risk level"""
        if bias_score > 70:
            return "CRITICAL"
        elif bias_score > 50:
            return "HIGH"
        elif bias_score > 30:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
