"""
Bias Calculation Utilities
Handles Disparate Impact Ratio (DIR) and Counterfactual Analysis
"""

import numpy as np
from typing import Dict, List, Tuple, Any


class BiasCalculator:
    """Calculate and analyze bias metrics"""
    
    @staticmethod
    def calculate_disparate_impact_ratio(
        group_a_favorable_rate: float,
        group_b_favorable_rate: float
    ) -> Tuple[float, str]:
        """
        Calculate Disparate Impact Ratio (DIR)
        DIR = P(Favorable | Group A) / P(Favorable | Group B)
        
        Standards:
        - DIR >= 0.8: Fair (safe harbor)
        - DIR < 0.8: Disparate Impact (potential discrimination)
        """
        if group_b_favorable_rate == 0:
            return float('inf'), "Undefined - Division by zero"
        
        dir_ratio = group_a_favorable_rate / group_b_favorable_rate
        
        if dir_ratio >= 0.8:
            status = "FAIR - Within Safe Harbor (80% Rule)"
        else:
            status = f"DISPARATE IMPACT DETECTED - {dir_ratio:.2%} of group B favorable rate"
        
        return dir_ratio, status
    
    @staticmethod
    def counterfactual_audit(
        original_score: float,
        proxy_data: Dict[str, Any],
        modified_proxy_data: Dict[str, Any],
        model_scoring_func
    ) -> Dict[str, Any]:
        """
        Perform counterfactual analysis
        Question: "What if we changed the proxy data (e.g., Zip Code)?"
        """
        original_outcome = model_scoring_func(original_score, proxy_data)
        modified_outcome = model_scoring_func(original_score, modified_proxy_data)
        
        score_changed = original_outcome != modified_outcome
        
        return {
            "original_score": original_outcome,
            "modified_score": modified_outcome,
            "score_changed": score_changed,
            "proxy_bit_flipped": True,
            "bias_indicator": "Proxy Bias Detected" if score_changed else "No Proxy Bias"
        }
    
    @staticmethod
    def calculate_statistical_parity(
        original_profile: Dict[str, float],
        modified_profile: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calculate statistical parity difference
        Measures difference in favorable outcome rates between groups
        """
        stat_parity_diff = original_profile.get("favorable_rate", 0) - modified_profile.get("favorable_rate", 0)
        
        return {
            "statistical_parity_difference": stat_parity_diff,
            "acceptable": abs(stat_parity_diff) <= 0.1,  # 10% threshold
            "risk_level": "HIGH" if abs(stat_parity_diff) > 0.15 else "MEDIUM" if abs(stat_parity_diff) > 0.1 else "LOW"
        }
    
    @staticmethod
    def generate_bias_score(
        dir_ratio: float,
        counterfactual_result: Dict[str, Any],
        statistical_parity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive bias score (0-100)
        High score = more biased
        """
        # DIR component (0-40 points)
        dir_score = min(40, max(0, (1 - dir_ratio) * 50)) if dir_ratio < 1 else 0
        
        # Counterfactual component (0-30 points)
        cf_score = 30 if counterfactual_result.get("score_changed") else 0
        
        # Statistical parity component (0-30 points)
        sp_diff = abs(statistical_parity.get("statistical_parity_difference", 0))
        sp_score = min(30, sp_diff * 100)
        
        total_bias_score = dir_score + cf_score + sp_score
        
        return {
            "total_bias_score": min(100, total_bias_score),
            "components": {
                "disparate_impact_score": dir_score,
                "counterfactual_score": cf_score,
                "statistical_parity_score": sp_score
            },
            "risk_level": "CRITICAL" if total_bias_score > 70 else "HIGH" if total_bias_score > 50 else "MEDIUM" if total_bias_score > 30 else "LOW"
        }
