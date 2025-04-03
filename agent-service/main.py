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

class AgentRequest(BaseModel):
    input: str
    sessionId: str
    context: Dict[str, Any] = {}

@app.post("/agent")
async def run_agent(data: AgentRequest):
    context = data.context or {}
    result = await Runner.run(orchestrator_agent, data.input, context=context)
    
    # Debug logging
    print("Result type:", type(result.final_output))
    print("Result value:", result.final_output)
    
    # Try to parse string representation of dict if needed
    if isinstance(result.final_output, str):
        try:
            import ast
            message = ast.literal_eval(result.final_output)
        except (SyntaxError, ValueError):
            message = {
                "type": "chat",
                "role": "assistant",
                "content": result.final_output
            }
    elif isinstance(result.final_output, dict):
        message = result.final_output
    else:
        message = {
            "type": "chat",
            "role": "assistant",
            "content": result.final_output
        }

    return {
        "messages": [message],
        "context": context,
        "sessionId": data.sessionId
    }
