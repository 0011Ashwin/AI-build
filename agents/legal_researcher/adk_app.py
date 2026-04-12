"""
Legal Researcher ADK Application
"""

from google.adk import adk_app
from agent import LegalResearcherAgent
import json


def create_adk_app():
    """Create ADK application for Legal Researcher"""
    
    researcher = LegalResearcherAgent()
    
    app = adk_app.ADKApp(
        name="legal_researcher",
        description="Legal Research and Precedent Retrieval Agent",
        version="1.0.0"
    )
    
    @app.route("/research", methods=["POST"])
    async def handle_research_request(request):
        """Handle legal research request"""
        audit_findings = await request.json()
        result = await researcher.research_bias(audit_findings)
        return {"research_result": result}
    
    @app.route("/tools/query-precedents", methods=["POST"])
    async def query_precedents(request):
        """Query legal precedents"""
        data = await request.json()
        result = await researcher._query_precedents(data.get("bias_type", ""))
        return {"precedents": result}
    
    return app


if __name__ == "__main__":
    app = create_adk_app()
    app.run()
