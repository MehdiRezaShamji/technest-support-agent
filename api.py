from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import Agent

app = FastAPI()


class ChatRequest(BaseModel):
    query: str
    session_id: str


agent = Agent()


@app.post("/chat")
def chat(req: ChatRequest):
    agent.add_message("user", req.query)
    while True:
        call_llm_result = agent.call_llm()
        if call_llm_result is None:
            raise HTTPException(status_code=500, detail=agent.last_error)
        if call_llm_result.get("tool_calls"):
            agent.run_tool(call_llm_result)
        else:
            return call_llm_result["content"]
