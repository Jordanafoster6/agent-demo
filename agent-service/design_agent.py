# agent-service/design_agent.py
from openai import AsyncOpenAI
from agents import Agent, function_tool, RunContextWrapper
from dotenv import load_dotenv
from context.design import create_design_context
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in .env")

client = AsyncOpenAI(api_key=api_key)

@function_tool
async def generate_image(context: RunContextWrapper[dict], prompt: str) -> dict:
    """
    Generate an image using OpenAI DALL·E 3 and return a structured design message.
    
    Args:
        context: The run context wrapper.
        prompt: The design prompt from the user.
    
    Returns:
        Dict with type 'design' and image details.
    """
    print("generate_image called with prompt:", prompt)
    response = await client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    url = response.data[0].url
    design_message = {
        "type": "design",
        "role": "assistant",
        "imageUrl": url,
        "message": "Here's your design!",
        "status": "refining",
        "originalPrompt": prompt,
        "currentPrompt": prompt,
    }
    context.context["design"] = create_design_context(url, prompt)
    return design_message

design_agent = Agent(
    name="DesignAgent",
    instructions=(
        """
        You are a design agent that generates images using OpenAI's DALL·E. 
        When you receive a prompt, use the generate_image tool to create the image. 
        Return the tool's output dictionary as-is with type 'design'.
        """
    ),
    tools=[generate_image],
    model="gpt-4",
    tool_use_behavior="run_llm_again"
)
