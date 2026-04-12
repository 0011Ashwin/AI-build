"""
Report Generation for Final Audit Reports
Generates PDF documents and structured verdicts
"""

from typing import Dict, Any, List
import json
from datetime import datetime


class ReportGenerator:
    """Generate final audit reports and verdicts"""
    
    @staticmethod
    def generate_verdict(
        bias_score: float,
        jury_consensus: Dict[str, Any],
        legal_context: List[Dict[str, Any]],
        quantitative_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate final verdict based on all analysis
        
        Returns: "Fair" or "Unfair"
        """
        # Determine verdict based on bias score and jury consensus
        juror_verdicts = jury_consensus.get("individual_verdicts", {})
        unfair_count = sum(1 for v in juror_verdicts.values() if v == "Unfair")
        fair_count = len(juror_verdicts) - unfair_count
        
        # Consensus voting
        if unfair_count >= 2:
            verdict = "UNFAIR"
            confidence = min(0.99, (unfair_count / len(juror_verdicts)) + 0.1)
        elif unfair_count == 1:
            verdict = "FAIR WITH CONCERNS"
            confidence = 0.6
        else:
            verdict = "FAIR"
            confidence = fair_count / len(juror_verdicts)
        
        return {
            "verdict": verdict,
            "confidence": confidence,
            "juror_votes": juror_verdicts,
            "bias_score": bias_score,
            "reasoning": jury_consensus.get("debate_summary", "")
        }
    
    @staticmethod
    def generate_bias_corrected_score(
        original_score: float,
        bias_severity: float,
        mitigation_factor: float = 0.5
    ) -> float:
        """
        Generate bias-corrected score
        Adjusts original score based on detected bias
        """
        adjustment = (bias_severity / 100) * (original_score * mitigation_factor)
        corrected_score = original_score - adjustment
        
        return max(0, min(100, corrected_score))
    
    @staticmethod
    def generate_pdf_report(
        case_data: Dict[str, Any],
        verdict: Dict[str, Any],
        quantitative_analysis: Dict[str, Any],
        legal_context: List[Dict[str, Any]],
        jury_debate: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate structured PDF report content
        In production, use reportlab or similar for actual PDF generation
        """
        report_content = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                     JUSTICE AI AUDIT REPORT                                   ║
║                    Fairness-First Algorithmic Auditing                        ║
╚═══════════════════════════════════════════════════════════════════════════════╝

REPORT METADATA
───────────────────────────────────────────────────────────────────────────────
Generated: {datetime.now().isoformat()}
Case ID: {case_data.get('case_id', 'N/A')}
Subject: {case_data.get('decision_type', 'N/A')}
Jurisdiction: {case_data.get('jurisdiction', 'N/A')}


STATE 1: INTAKE NODE
───────────────────────────────────────────────────────────────────────────────
Name: {case_data.get('name', 'N/A')}
Age: {case_data.get('age', 'N/A')}
Priors: {case_data.get('priors', 'N/A')}
Proxy Data (Zip Code): {case_data.get('zip_code', 'N/A')}


STATE 2: AUDIT CHAMBER - QUANTITATIVE ANALYSIS
───────────────────────────────────────────────────────────────────────────────
Disparate Impact Ratio: {quantitative_analysis.get('dir_ratio', 'N/A')}
Status: {quantitative_analysis.get('dir_status', 'N/A')}

Counterfactual Analysis:
- Original Score: {quantitative_analysis.get('original_score', 'N/A')}
- Modified Score (Proxy Flipped): {quantitative_analysis.get('modified_score', 'N/A')}
- Score Changed: {quantitative_analysis.get('score_changed', 'N/A')}
- Bias Indicator: {quantitative_analysis.get('bias_indicator', 'N/A')}

Bias Score: {quantitative_analysis.get('bias_score', 'N/A')}/100
Risk Level: {quantitative_analysis.get('risk_level', 'N/A')}


STATE 3: CONTEXTUAL RAG - LEGAL PRECEDENTS
───────────────────────────────────────────────────────────────────────────────
Retrieved Legal Context:
"""
        
        for i, precedent in enumerate(legal_context[:3], 1):
            report_content += f"""
{i}. {precedent.get('case', precedent.get('title', 'N/A'))}
   Year: {precedent.get('year', 'N/A')}
   Summary: {precedent.get('summary', 'N/A')}
   Relevance: {precedent.get('relevance_score', 'N/A')}
"""
        
        report_content += f"""

STATE 4: JURY VERDICT - MULTI-AGENT DEBATE
───────────────────────────────────────────────────────────────────────────────
Debate Summary:
{jury_debate.get('debate_summary', 'N/A')}

Individual Juror Verdicts:
- Mitigator Juror (Defense): {jury_debate.get('individual_verdicts', {}).get('mitigator', 'N/A')}
- Strict Auditor Juror (Prosecutor): {jury_debate.get('individual_verdicts', {}).get('auditor', 'N/A')}
- Ethicist Juror: {jury_debate.get('individual_verdicts', {}).get('ethicist', 'N/A')}


STATE 5: FINAL VERDICT & MITIGATION
───────────────────────────────────────────────────────────────────────────────
FINAL VERDICT: {verdict.get('verdict', 'N/A')}
Confidence: {verdict.get('confidence', 'N/A'):.1%}

Bias Score: {verdict.get('bias_score', 'N/A')}/100
Original Score: {case_data.get('original_score', 'N/A')}
Bias-Corrected Score: {quantitative_analysis.get('corrected_score', 'N/A')}

Key Reasoning:
{verdict.get('reasoning', 'N/A')}

AUDIT CONCLUSION
───────────────────────────────────────────────────────────────────────────────
This algorithmic decision has been audited for fairness using a multi-agent 
debate system with:
✓ Quantitative bias analysis
✓ Counterfactual testing
✓ Legal precedent review
✓ Multi-perspective LLM evaluation
✓ SDG 10 & 16 alignment assessment

Recommendation: {verdict.get('verdict', 'N/A')}

═══════════════════════════════════════════════════════════════════════════════
Report Generated by: Justice AI Audit System v1.0
═══════════════════════════════════════════════════════════════════════════════
"""
        
        return {
            "report_content": report_content,
            "verdict": verdict.get("verdict", "UNKNOWN"),
            "confidence": verdict.get("confidence", 0),
            "case_id": case_data.get("case_id", "N/A"),
            "generated_at": datetime.now().isoformat()
        }
