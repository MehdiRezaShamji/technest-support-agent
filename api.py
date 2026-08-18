import os
import json
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from main import Agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
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


sessions: dict[str, Agent] = {}


def get_agent(session_id: str) -> Agent:
    if session_id not in sessions:
        sessions[session_id] = Agent(session_id)
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
            tool_used = call_llm_result["tool_calls"][-1]["function"]["name"]
        else:
            agent.save_memory()
            return ChatResponse(
                session_id=session_id,
                reply=call_llm_result["content"],
                tool_used=tool_used,
            )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/conversations")
def get_conversations():
    conversations = []

    for filename in os.listdir("."):
        if filename.startswith("conversation_") and filename.endswith(".json"):
            session_id = filename[len("conversation_") : -len(".json")]

            conversations.append(
                {
                    "session_id": session_id,
                    "conversation": f"/conversation/{session_id}",
                }
            )

    return {"total_conversations": len(conversations), "conversations": conversations}


@app.get("/conversation/{session_id}")
def get_conversation(session_id: str):
    filename = f"conversation_{session_id}.json"

    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="Conversation not found")

    with open(filename, "r") as file:
        conversation = json.load(file)

    return {"session_id": session_id, "conversation": conversation}
