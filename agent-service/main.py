from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
from agents import Runner
from orchestrator_agent import orchestrator_agent
import json

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify your frontend origin(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    # Process final_output
    if 'context_length_exceeded' in str(result.final_output):
        message = {
            "type": "chat",
            "role": "assistant",
            "content": "The response from Printify is too large to process at once. Please ask for specific details or a summary."
        }
    elif isinstance(result.final_output, dict) and "type" in result.final_output:
        message = result.final_output  # Pass the agent's output as-is
    elif isinstance(result.final_output, str):
        try:
            # Parse JSON string into a dictionary
            message = json.loads(result.final_output)
            if not isinstance(message, dict) or "type" not in message:
                raise ValueError("Parsed output is not a valid message dictionary")
        except (json.JSONDecodeError, ValueError):
            # Fallback to chat if parsing fails or result isn’t a valid message
            message = {
                "type": "chat",
                "role": "assistant",
                "content": result.final_output
            }
    else:
        # Default to chat for other types
        message = {
            "type": "chat",
            "role": "assistant",
            "content": str(result.final_output)
        }

    return {
        "sessionId": req.sessionId,
        "messages": [message],
        "context": context,
    }
