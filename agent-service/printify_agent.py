import os
import httpx
from typing import List, Union
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
async def select_blueprint(ctx: RunContextWrapper[dict], user_reply: str) -> dict:
    """
    Matches user's response to a blueprint from previous matches and saves it to product context.
    """
    blueprint_matches = ctx.context.get("blueprint_matches", [])
    user_reply_lower = user_reply.strip().lower()

    # Try to match by ID or fuzzy title
    selected = None
    for bp in blueprint_matches:
        if user_reply_lower == str(bp["id"]):
            selected = bp
            break
        if user_reply_lower in bp["title"].lower():
            selected = bp
            break

    if not selected:
        return {
            "type": "chat",
            "role": "assistant",
            "content": "Hmm, I couldn't find that product. Please respond with the name or Blueprint ID of one of the suggestions I gave you."
        }

    # Store in context under product
    ctx.context["product"] = {
        "blueprint_id": selected["id"],
        "blueprint_name": selected["title"],
    }

    return {
        "type": "chat",
        "role": "assistant",
        "content": f"Great choice! You've selected: {selected['title']} (ID: {selected['id']}). Next, I'll find the best print providers for this product..."
    }

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

@function_tool
async def handle_printify_prompt(ctx: RunContextWrapper[dict], input: str) -> dict:
    ctx.context["last_prompt"] = input
    blueprint_matches = ctx.context.get("blueprint_matches", [])

    # Try to parse as int (ID)
    try:
        blueprint_id = int(input)
        return await select_blueprint(ctx, blueprint_id)
    except ValueError:
        pass

    # Try to match name
    for bp in blueprint_matches:
        if input.strip().lower() in bp["title"].lower():
            return await select_blueprint(ctx, input)

    # If no match, assume it's a fresh product request
    return await get_matching_blueprints(ctx, input)

printify_agent = Agent(
    name="PrintifyAgent",
    instructions="""
    You are the PrintifyAgent.

    When a user describes a product, call `get_matching_blueprints`.

    If the user replies with a name or blueprint ID from the list, call `select_blueprint`.

    Never respond manually — always use tools to fetch or select blueprints.
    """,
    tools=[handle_printify_prompt, get_matching_blueprints, select_blueprint],
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