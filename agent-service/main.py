from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
from agents import Runner
from orchestrator_agent import orchestrator_agent

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify your frontend origin(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# class AgentRequest(BaseModel):
#     input: str
#     sessionId: str
#     context: Dict[str, Any] = {}

class PromptRequest(BaseModel):
    input: str
    sessionId: str
    context: Dict[str, Any] = {}

@app.post("/agent")
async def run_agent(req: PromptRequest):
    context = req.context or {}
    result = await Runner.run(orchestrator_agent, req.input, context=context)
    
    # Debug logging
    print("Result type:", type(result.final_output))
    print("Result value:", result.final_output)

    message = {
      "type": "chat",
      "role": "assistant",
      "content": result.final_output
    }

    return {
        "sessionId": req.sessionId,
        "messages": [message],
        "context": context,
    }
