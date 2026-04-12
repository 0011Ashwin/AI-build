"""
Ethicist Juror ADK Application
"""

from google.adk import adk_app
from agent import EthicistJurorAgent


def create_adk_app():
    """Create ADK application for Ethicist Juror"""
    
    ethicist = EthicistJurorAgent()
    
    app = adk_app.ADKApp(
        name="ethicist_juror",
        description="Ethicist Juror - Human Impact & SDG Alignment",
        version="1.0.0"
    )
    
    @app.route("/evaluate", methods=["POST"])
    async def handle_evaluation(request):
        """Handle case evaluation"""
        case_context = await request.json()
        result = await ethicist.evaluate_case(case_context)
        return {"verdict": result}
    
    return app


if __name__ == "__main__":
    app = create_adk_app()
    app.run()
