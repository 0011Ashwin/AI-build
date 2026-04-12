"""
Chief Justice ADK Application
"""

from google.adk import adk_app
from agent import ChiefJusticeAgent
import os
import json


def create_adk_app():
    """Create ADK application for Chief Justice Agent"""
    
    chief_justice = ChiefJusticeAgent()
    
    app = adk_app.ADKApp(
        name="chief_justice_orchestrator",
        description="Main orchestrator for Justice AI Workflow",
        version="1.0.0"
    )
    
    @app.route("/audit", methods=["POST"])
    async def handle_audit_request(request):
        """Handle incoming audit case"""
        case_data = await request.json()
        result = await chief_justice.orchestrate_audit(case_data)
        return {"result": result}
    
    @app.route("/status", methods=["GET"])
    async def get_workflow_status(request):
        """Get current workflow status"""
        return {"state": chief_justice.workflow_state}
    
    return app


if __name__ == "__main__":
    app = create_adk_app()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
