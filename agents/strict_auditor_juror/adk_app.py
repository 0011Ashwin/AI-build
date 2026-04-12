"""
Strict Auditor Juror ADK Application
"""

from google.adk import adk_app
from agent import StrictAuditorJurorAgent
import os


def create_adk_app():
    """Create ADK application for Strict Auditor Juror"""
    
    auditor = StrictAuditorJurorAgent()
    
    app = adk_app.ADKApp(
        name="strict_auditor_juror",
        description="Strict Auditor Juror - Prosecutor Perspective",
        version="1.0.0"
    )
    
    @app.route("/evaluate", methods=["POST"])
    async def handle_evaluation(request):
        """Handle case evaluation"""
        case_context = await request.json()
        result = await auditor.evaluate_case(case_context)
        return {"verdict": result}
    
    return app


if __name__ == "__main__":
    app = create_adk_app()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
