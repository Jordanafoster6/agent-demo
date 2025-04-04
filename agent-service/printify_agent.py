import os
import httpx
from typing import List
from dotenv import load_dotenv
from context.product import ProductContext
from agents import Agent, function_tool, RunContextWrapper

load_dotenv()

PRINTIFY_API_KEY = os.getenv("PRINTIFY_API_KEY")
if not PRINTIFY_API_KEY:
    raise ValueError("PRINTIFY_API_KEY is not set in .env")

printify_shop_id = os.getenv("PRINTIFY_SHOP_ID")
if not printify_shop_id:
    raise ValueError("PRINTIFY_SHOP_ID is not set in .env")

@function_tool
async def get_matching_blueprints(ctx: RunContextWrapper[dict], prompt: str) -> dict:
    """
    Fetch Printify blueprints and match against the user prompt to suggest products.
    """
    # Step 1: Fetch blueprints
    headers = {"Authorization": f"Bearer {PRINTIFY_API_KEY}"}
    async with httpx.AsyncClient() as client:
        res = await client.get("https://api.printify.com/v1/catalog/blueprints.json", headers=headers)
        res.raise_for_status()
        blueprints = res.json()

    # Step 2: Match based on simple fuzzy matching against title
    prompt_lower = prompt.lower()
    matches = [
        bp for bp in blueprints
        if any(keyword in prompt_lower for keyword in bp["title"].lower().split())
    ]

    # Step 3: Sort matches (basic heuristic: by match count)
    ranked_matches = sorted(matches, key=lambda b: sum(kw in prompt_lower for kw in b["title"].lower().split()), reverse=True)
    top_matches = ranked_matches[:5]

    # Step 4: Store in context for follow-ups
    ctx.context["blueprint_matches"] = top_matches  # not typed, short-lived cache

    # Step 5: Build structured message
    content_lines = ["Based on your description, I found these product options:\n"]
    for bp in top_matches:
        content_lines.append(f"• {bp['title']} (Blueprint ID: {bp['id']})")

    content_lines.append("\nWhich one of these would you like to use? You can reply with the name or Blueprint ID.")
    return {
        "type": "chat",
        "role": "assistant",
        "content": "\n".join(content_lines)
    }

printify_agent = Agent(
    name="PrintifyAgent",
    instructions="You are a Printify product creation assistant. Use tools to search blueprints, configure variants, and create products. Always confirm before finalizing.",
    tools=[get_matching_blueprints],
    model="gpt-4",
    tool_use_behavior="run_llm_again"
)


# ------------------------------------------------------------
#  Improvements
# ------------------------------------------------------------

# Future Tools:
# - Add tool to fetch product details from Printify
# - Add tool to create product in Printify
# - Add tool to update product in Printify
# - Add tool to delete product in Printify
# - Add tool to list products in Printify

# Future Enhancements:
# - Use OpenAI function calling or embeddings for better semantic matches
# - Cache the blueprint catalog (it doesn’t change often)
# - Filter out non-physical products or kids' stuff


# ------------------------------------------------------------
#  Old Working Base Agent
# ------------------------------------------------------------

# @function_tool
# async def mock_printify_response(ctx: RunContextWrapper[dict], prompt: str) -> dict:
#     """
#     Mock tool to simulate initial Printify response for blueprint matching.
#     """
#     product = ctx.context.get("product", {}) 
#     # For now, this is just a placeholder to prove routing is working
#     return {
#         "type": "chat",
#         "role": "assistant",
#         "content": f"(PrintifyAgent) You said: '{prompt}'. Blueprint selection coming soon."
#     }
# printify_agent = Agent(
#     name="PrintifyAgent",
#     instructions="You are a Printify product creation assistant. Use tools to search for blueprints, select variants, and create products.",
#     tools=[mock_printify_response],
#     model="gpt-4",
#     tool_use_behavior="run_llm_again"
# )