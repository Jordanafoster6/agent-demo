from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from agents import Runner
from orchestrator_agent import orchestrator_agent
import json
import uuid

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory context store (use Redis in production)
context_store: Dict[str, Dict[str, Any]] = {}

class PromptRequest(BaseModel):
    input: str
    sessionId: Optional[str] = None
    context: Dict[str, Any] = {}

@app.post("/agent")
async def run_agent(req: PromptRequest):
    # Generate or use session ID
    session_id = req.sessionId or str(uuid.uuid4())
    context = context_store.get(session_id, req.context or {})
    
    try:
        result = await Runner.run(orchestrator_agent, req.input, context=context)
        message = result.final_output
        
        if 'context_length_exceeded' in str(message):
            raise HTTPException(status_code=400, detail="The response from Printify is too large. Please ask for specific details or a summary.")
        elif isinstance(message, dict) and "type" in message:
            pass  # Use as-is
        elif isinstance(message, str):
            try:
                message = json.loads(message)
                if not isinstance(message, dict) or "type" not in message:
                    raise ValueError
            except (json.JSONDecodeError, ValueError):
                message = {"type": "chat", "role": "assistant", "content": message}
        else:
            message = {"type": "chat", "role": "assistant", "content": str(message)}
        
        # Update context store
        context_store[session_id] = context
        
        return {
            "sessionId": session_id,
            "messages": [message],
            "context": context,
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        status_code = 429 if "rate limit" in str(e).lower() else 500
        raise HTTPException(status_code=status_code, detail=str(e))
    