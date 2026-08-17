"""
FastAPI wrapper for the TechNest Support Agent, built on top of your
existing Agent class in main.py.

Fixes vs. a single shared `agent = Agent()`:
- One Agent instance per session_id (sessions dict below), so concurrent
  users don't share conversation history.
- /chat returns a JSON object {reply, tool_used, session_id} instead of a
  bare string, since the frontend reads data.reply / data.tool_used.
- CORS enabled so a browser-based frontend on a different origin can call this.
- Retry loop restored (matches the "Automatic retry for failed LLM requests"
  feature from your README) instead of failing on the first bad response.
- /health added for the frontend's connection-status indicator.

Run locally: uvicorn api:app --reload
On Render:   uvicorn api:app --host 0.0.0.0 --port $PORT
"""

from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from main import Agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # Tighten this to your actual frontend origin once deployed,
    # e.g. ["https://your-frontend.vercel.app"]
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    query: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    tool_used: str | None = None


# One Agent per session_id, so concurrent users don't share memory.
# NOTE: resets on server restart — fine for a demo, swap for a real DB later.
sessions: dict[str, Agent] = {}


def get_agent(session_id: str) -> Agent:
    if session_id not in sessions:
        sessions[session_id] = Agent()
    return sessions[session_id]


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="query cannot be empty")

    session_id = req.session_id or str(uuid4())
    agent = get_agent(session_id)
    agent.add_message("user", req.query)

    tool_used = None
    max_tries = 2

    while True:
        call_llm_result = None
        for _ in range(max_tries):
            call_llm_result = agent.call_llm()
            if call_llm_result is not None:
                break
        if call_llm_result is None:
            raise HTTPException(status_code=500, detail=agent.last_error)

        if call_llm_result.get("tool_calls"):
            agent.run_tool(call_llm_result)
            # remember the last tool name used this turn, to surface in the UI
            tool_used = call_llm_result["tool_calls"][-1]["function"]["name"]
        else:
            return ChatResponse(
                session_id=session_id,
                reply=call_llm_result["content"],
                tool_used=tool_used,
            )


@app.get("/health")
def health():
    return {"status": "ok"}
