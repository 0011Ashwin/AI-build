"""
Legal Researcher Agent - State 3 (RAG)
Retrieves legal precedents and contextual information
"""

from google.adk import agent
from typing import Dict, Any, List
import sys
sys.path.append('../..')
from shared.vector_search_client import VectorSearchClient


class LegalResearcherAgent:
    """
    State 3 Handler: Contextual RAG
    Retrieves legal precedents and guidelines from Vector Database
    """
    
    def __init__(self, project_id: str = "justice-ai-project"):
        self.agent = agent.Agent(
            name="legal_researcher",
            model="gemini-1.5-pro",
            max_steps=5
        )
        self.vector_search = VectorSearchClient(project_id)
    
    def get_instructions(self) -> str:
        """System instructions for Legal Researcher"""
        return """You are the Legal Researcher, a paralegal AI specializing in algorithmic fairness law.

Your responsibilities:
1. Analyze bias findings from the Quantitative Auditor
2. Search legal databases for relevant precedents
3. Retrieve applicable sentencing guidelines (if relevant)
4. Find comparable historical cases
5. Identify SDG 10/16 alignment issues
6. Provide citations and legal context

You must:
- Search by bias type (gender, racial, credit, etc.)
- Prioritize recent and landmark cases
- Extract relevant legal standards
- Provide confidence scores for relevance

Output format (JSON):
{
    "bias_type_identified": "gender_bias",
    "relevant_precedents": [...],
    "applicable_guidelines": {...},
    "comparable_cases": [...],
    "sdg_alignment": {...},
    "legal_summary": "..."
}
"""
    
    async def research_bias(self, audit_findings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Research legal context for identified bias
        
        Args:
            audit_findings: Bias findings from Quantitative Auditor
        
        Returns:
            Legal precedents and context
        """
        bias_type = self._identify_bias_type(audit_findings)
        
        research_result = {
            "bias_type": bias_type,
            "research_timestamp": self._get_timestamp(),
            "legal_context": {}
        }
        
        # Query precedents
        precedents = await self._query_precedents(bias_type)
        research_result["legal_context"]["precedents"] = precedents
        
        # Query sentencing guidelines (if applicable)
        guidelines = await self._query_sentencing_guidelines(audit_findings)
        research_result["legal_context"]["guidelines"] = guidelines
        
        # Retrieve comparable cases
        comparable_cases = await self._retrieve_comparable_cases(audit_findings)
        research_result["legal_context"]["comparable_cases"] = comparable_cases
        
        # Check SDG alignment
        sdg_check = await self._check_sdg_alignment(bias_type)
        research_result["legal_context"]["sdg_alignment"] = sdg_check
        
        return research_result
    
    def _identify_bias_type(self, audit_findings: Dict[str, Any]) -> str:
        """Identify the type of bias detected"""
        bias_score = audit_findings.get("bias_score", 0)
        
        # Simulate bias type detection
        if "gender" in str(audit_findings).lower():
            return "gender_bias"
        elif "race" in str(audit_findings).lower():
            return "racial_bias"
        elif "credit" in str(audit_findings).lower():
            return "credit_bias"
        else:
            return "algorithmic_fairness"
    
    async def _query_precedents(self, bias_type: str) -> List[Dict[str, Any]]:
        """Query legal precedents"""
        precedents = self.vector_search.query_legal_context(
            bias_type=bias_type,
            query_text=f"Legal precedents for {bias_type}",
            top_k=3
        )
        return precedents
    
    async def _query_sentencing_guidelines(
        self,
        audit_findings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Query sentencing guidelines"""
        guidelines = self.vector_search.query_sentencing_guidelines(
            jurisdiction="US Federal",
            offense_type="Algorithmic Discrimination"
        )
        return guidelines
    
    async def _retrieve_comparable_cases(
        self,
        audit_findings: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Retrieve comparable historical cases"""
        comparable = self.vector_search.retrieve_comparable_cases(
            defendant_profile=audit_findings,
            limit=3
        )
        return comparable
    
    async def _check_sdg_alignment(self, bias_type: str) -> Dict[str, Any]:
        """Check alignment with UN Sustainable Development Goals"""
        sdg_10_precedents = self.vector_search.query_legal_context(
            bias_type="sdg_10",
            query_text="SDG 10 - Reduce Inequalities",
            top_k=2
        )
        
        return {
            "sdg_10_alignment": {
                "goal": "Reduce Inequalities",
                "alignment_score": 0.75,
                "relevant_guidelines": sdg_10_precedents
            },
            "sdg_16_alignment": {
                "goal": "Peace, Justice and Strong Institutions",
                "alignment_score": 0.82,
                "note": "Algorithmic fairness supports institutional trust"
            }
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
