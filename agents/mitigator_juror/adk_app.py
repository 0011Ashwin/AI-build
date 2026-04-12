"""
Mitigator Juror ADK Application
"""

from google.adk import adk_app
from agent import MitigatorJurorAgent
import os


def create_adk_app():
    """Create ADK application for Mitigator Juror"""
    
    mitigator = MitigatorJurorAgent()
    
    app = adk_app.ADKApp(
        name="mitigator_juror",
        description="Mitigator Juror - Defense Perspective",
        version="1.0.0"
    )
    
    @app.route("/evaluate", methods=["POST"])
    async def handle_evaluation(request):
        """Handle case evaluation"""
        case_context = await request.json()
        result = await mitigator.evaluate_case(case_context)
        return {"verdict": result}
    
    return app


if __name__ == "__main__":
    app = create_adk_app()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
