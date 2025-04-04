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
async def generate_image(ctx: RunContextWrapper[dict], prompt: str) -> dict:
    """
    Generate an image using OpenAI DALL·E 3 and then return a structured design message.
    """
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

    # Set the design context using the shared function
    ctx.context["design"] = create_design_context(url, prompt)

    return design_message

design_agent = Agent(
    name="DesignAgent",
    instructions="You are a design agent that generates images using OpenAI's DALL·E. When you receive a prompt, use the generate_image tool to create the image. The tool will return a structured design message. You must return this exact message as your response, not as a string or content. The message should be a dictionary with type 'design', not a string representation of a dictionary.",
    tools=[generate_image],
    model="gpt-4",
    tool_use_behavior="run_llm_again"
)
