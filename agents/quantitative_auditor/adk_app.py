"""
Quantitative Auditor ADK Application
"""

from google.adk import adk_app
from agent import QuantitativeAuditorAgent
import json


def create_adk_app():
    """Create ADK application for Quantitative Auditor"""
    
    auditor = QuantitativeAuditorAgent()
    
    app = adk_app.ADKApp(
        name="quantitative_auditor",
        description="Quantitative Bias Analysis Agent",
        version="1.0.0"
    )
    
    @app.route("/analyze", methods=["POST"])
    async def handle_analysis_request(request):
        """Handle case analysis request"""
        case_data = await request.json()
        result = await auditor.analyze_case(case_data)
        return {"analysis": result}
    
    @app.route("/tools/calculate-dir", methods=["POST"])
    async def calculate_dir(request):
        """Calculate Disparate Impact Ratio"""
        data = await request.json()
        result = await auditor._calculate_disparate_impact(data)
        return {"result": result}
    
    return app


if __name__ == "__main__":
    app = create_adk_app()
    app.run()
