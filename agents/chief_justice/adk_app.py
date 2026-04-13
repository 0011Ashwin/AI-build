"""
Chief Justice — Cloud Run HTTP wrapper.
Delegates the full audit pipeline via the ADK Runner.
"""
import os, sys, json, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

app = FastAPI(title="Chief Justice Agent", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── ADK runner ────────────────────────────────────────────────────────────────
try:
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai.types import Content, Part
    from agent import root_agent

    _session_service = InMemorySessionService()
    _runner = Runner(agent=root_agent, app_name="justice-ai", session_service=_session_service)
    _adk_ok = True
    print(f"✅ Chief Justice runner loaded ({len(root_agent.sub_agents)} sub-agents)")
except Exception as e:
    print(f"WARNING: ADK runner failed ({e}). Returning 503 on /audit calls.")
    _adk_ok = False
    _runner = None
    _session_service = None


@app.get("/health")
async def health():
    return {"status": "healthy", "agent": "chief_justice", "adk_ready": _adk_ok}


@app.post("/audit")
async def audit(case_data: Dict[str, Any]):
    """Run the full 5-stage audit pipeline for a submitted case."""
    if not _adk_ok:
        raise HTTPException(503, "ADK runner not initialised — check GOOGLE_API_KEY")
    try:
        session_id = f"audit-{case_data.get('case_id','x')}-{uuid.uuid4().hex[:8]}"
        user_id = "cloud-run-client"
        await _session_service.create_session(app_name="justice-ai", user_id=user_id, session_id=session_id)
        prompt = f"Run a full fairness audit on this case:\n{json.dumps(case_data, indent=2)}"
        message = Content(role="user", parts=[Part(text=prompt)])
        final_text = ""
        async for event in _runner.run_async(user_id=user_id, session_id=session_id, new_message=message):
            if hasattr(event, 'content') and event.content:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        final_text += part.text
        # Try to return parsed JSON, else raw text
        try:
            clean = final_text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            return {"result": json.loads(clean)}
        except Exception:
            return {"result": {"raw_response": final_text}}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/status")
async def status():
    return {"state": "ready", "agent": "chief_justice", "sub_agents": [a.name for a in root_agent.sub_agents] if _adk_ok else []}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
