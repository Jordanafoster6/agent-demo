import os
import requests
from dotenv import load_dotenv
from agents import Agent, function_tool, RunContextWrapper

load_dotenv()

PRINTIFY_API_KEY = os.getenv("PRINTIFY_API_KEY")
if not PRINTIFY_API_KEY:
    raise ValueError("PRINTIFY_API_KEY is not set in .env")

printify_shop_id = os.getenv("PRINTIFY_SHOP_ID")
if not printify_shop_id:
    raise ValueError("PRINTIFY_SHOP_ID is not set in .env")

@function_tool
async def select_variants(ctx: RunContextWrapper[dict], selection: str) -> dict:
    """
    Handles the user's variant selection and stores it in the context.
    """
    print("select_variants called with selection:", selection)  # Log tool invocation
    if not ctx.context.get("awaiting_variant_selection", False):
      return {
        "type": "printify",
        "message": "No variant selection is currently awaited."
      }
    
    try:
      index = int(selection.split()[-1]) - 1  # Extract number from "Select variant X"
      selected_variant = ctx.context["variants_list"][index]
      ctx.context["selected_variant"] = selected_variant
      ctx.context["awaiting_variant_selection"] = False
      return {
        "type": "printify",
        "message": f"You have selected variant: {selected_variant['title']}"
      }
    except (IndexError, ValueError):
      return {
        "type": "printify",
        "message": "Invalid selection. Please try again with a valid number."
      }

@function_tool
async def get_variants(ctx: RunContextWrapper[dict]) -> dict:
    """
    Fetches variants for the selected blueprint and print provider from the context.
    """
    print("get_variants called with ctx")  # Log tool invocation
    if "selected_blueprint" not in ctx.context or "selected_print_provider" not in ctx.context:
      return {
        "type": "printify",
        "message": "Please select a blueprint and print provider first."
      }
    
    blueprint_id = ctx.context["selected_blueprint"]["id"]
    print_provider_id = ctx.context["selected_print_provider"]["id"]
    print("get_variants called with blueprint_id:", blueprint_id, "and print_provider_id:", print_provider_id)  # Log tool invocation
    url = f"https://api.printify.com/v1/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/variants.json"
    headers = {"Authorization": f"Bearer {PRINTIFY_API_KEY}"}
    try:
      response = requests.get(url, headers=headers)
      response.raise_for_status()
      variants = response.json()
      variant_names = [v["title"] for v in variants]
      ctx.context["variants_list"] = variants
      ctx.context["awaiting_variant_selection"] = True
      selection_message = (
        "Here are the available variants:\n" +
        "\n".join([f"{i+1}. {v}" for i, v in enumerate(variant_names)]) +
        "\nPlease select one by saying 'Select variant X' where X is the number."
      )
      return {
        "type": "printify",                                                                                                                                                                     
        "message": selection_message,
        "variants": variant_names
      }
    except requests.RequestException as e:
      return {
        "type": "printify",
        "message": f"Failed to fetch variants: {str(e)}"
      }
    
@function_tool
async def select_print_provider(ctx: RunContextWrapper[dict], selection: str) -> dict:
    """
    Handles the user's print provider selection and stores it in the context.
    """
    print("select_print_provider called with selection:", selection)  # Log tool invocation
    if not ctx.context.get("awaiting_print_provider_selection", False):
      return {
        "type": "printify",
        "message": "No print provider selection is currently awaited."
      }
    
    try:
      index = int(selection.split()[-1]) - 1  # Extract number from "Select print provider X"
      selected_pp = ctx.context["print_providers_list"][index]
      ctx.context["selected_print_provider"] = selected_pp
      ctx.context["awaiting_print_provider_selection"] = False
      return {
        "type": "printify",
        "message": f"You have selected print provider: {selected_pp['title']}"
      }
    except (IndexError, ValueError):
      return {
        "type": "printify",
        "message": "Invalid selection. Please try again with a valid number."
      }
    
@function_tool
async def get_print_providers(ctx: RunContextWrapper[dict]) -> dict:
    """
    Fetches print providers for the selected blueprint from the context.
    """
    print("get_print_providers called with ctx")  # Log tool invocation
    if "selected_blueprint" not in ctx.context:
      return {
        "type": "printify",
        "message": "No blueprint selected. Please select a blueprint first."
      }
    
    blueprint_id = ctx.context["selected_blueprint"]["id"]
    url = f"https://api.printify.com/v1/catalog/blueprints/{blueprint_id}/print_providers.json"
    headers = {"Authorization": f"Bearer {PRINTIFY_API_KEY}"}
    try:
      response = requests.get(url, headers=headers)
      response.raise_for_status()
      print_providers = response.json()
      print_provider_names = [pp["title"] for pp in print_providers]
      # Store the full list in context for selection
      ctx.context["print_providers_list"] = print_providers
      ctx.context["awaiting_print_provider_selection"] = True
      selection_message = (
        "Here are the available print providers:\n" +
        "\n".join([f"{i+1}. {pp}" for i, pp in enumerate(print_provider_names)]) +
        "\nPlease select one by saying 'Select print provider X' where X is the number."
      )
      return {
        "type": "printify",
        "message": selection_message,
        "printProviders": print_provider_names
      }
    except requests.RequestException as e:
      return {
        "type": "printify",
        "message": f"Failed to fetch print providers: {str(e)}"
      }
    
@function_tool
async def select_blueprint(ctx: RunContextWrapper[dict], selection: str) -> dict:
    """
    Handles the user's blueprint selection and stores it in the context.
    """
    print("select_blueprint called with selection:", selection)  # Log tool invocation
    if ctx.context.get("awaiting_selection", False):
      try:
        # Extract the number from the prompt, e.g., "Select blueprint 1"
        index = int(selection.split()[-1]) - 1
        selected_bp = ctx.context["blueprints_list"][index]
        ctx.context["selected_blueprint"] = selected_bp
        ctx.context["awaiting_selection"] = False
        print("Selected blueprint:", selected_bp["title"])  # Debug
        # Trigger next step explicitly if needed
        # return await get_print_providers(ctx)  # Chain to print providers
        return {
          "type": "printify",
          "message": f"You have selected: {selected_bp['title']}"
        }
      except (IndexError, ValueError):
        return {
          "type": "printify",
          "message": "Invalid selection. Please try again."
        }
    else:
      return {
        "type": "printify",
        "message": "No selection is currently awaited."
      }
@function_tool
async def get_blueprints(ctx: RunContextWrapper[dict], prompt: str) -> dict:
  """
  Fetches Printify blueprints, filters them based on the prompt, and prepares for selection.
  """
  print("get_blueprints called with prompt:", prompt)  # Log tool invocation
  url = "https://api.printify.com/v1/catalog/blueprints.json"
  headers = {"Authorization": f"Bearer {PRINTIFY_API_KEY}"}
  try:
      response = requests.get(url, headers=headers)
      response.raise_for_status()  # Raises exception for 4xx/5xx errors
      blueprints = response.json()
      num_blueprints = len(blueprints)
      print("Number of blueprints:", num_blueprints)
      sample_blueprint = [bp for bp in blueprints[:1]]
      # print("Sample blueprints:", sample_blueprint)
      # Extract keywords from prompt (simple split for now)
      keywords = prompt.lower().split()
      matched_blueprints = [
        bp for bp in blueprints
        if any(kw in bp["title"].lower() for kw in keywords)
      ]
      print("Number of matched blueprints:", len(matched_blueprints))
      if matched_blueprints:
        # Store the list in context for later selection
        ctx.context["blueprints_list"] = matched_blueprints
        ctx.context["awaiting_selection"] = True
        blueprint_names = [bp["title"] for bp in matched_blueprints]
        selection_message = "Here are the matching blueprints:\n" + "\n".join(
          [f"{i+1}. {bp}" for i, bp in enumerate(blueprint_names)]
        ) + "\nPlease select one by saying 'Select blueprint X' where X is the number."
        return {
          "type": "printify",
          "message": selection_message,
          "blueprints": blueprint_names
        }
      return {
          "type": "printify",
          "message": "No matching blueprints found"
      }
  except requests.RequestException as e:
      print("API call failed:", str(e))  # Log the error
      return {
          "type": "printify",
          "message": f"Failed to fetch blueprints: {str(e)}"
      }

# Define the Printify Product Agent
printify_agent = Agent(
    name="PrintifyProductAgent",
    instructions=(
      """
      You are a Printify assistant. Follow these steps:

      - When the user asks for products or blueprints (e.g., "I want a coffee mug"), use get_blueprints and return its result directly as a dictionary with 'type': 'printify'.
      - When the user says "Select blueprint X", use select_blueprint and return its result directly.
      - After a blueprint is selected, use get_print_providers and return its result directly.
      - When the user says "Select print provider Y", use select_print_provider and return its result directly.
      - After a print provider is selected, use get_variants and return its result directly.
      - When the user says "Select variant Z", use select_variants and return its result directly.

      Do not rephrase or convert tool outputs into plain text. Return them as-is with "type": "printify".
      """
    ),
    tools=[get_blueprints, select_blueprint, get_print_providers, select_print_provider, get_variants, select_variants],
    model="gpt-4",
    tool_use_behavior="run_llm_again"
)

# @function_tool
# async def get_print_providers(ctx: RunContextWrapper[dict]) -> dict:
#     blueprint = ctx.context.get("selected_blueprint")
#     if not blueprint:
#         raise ValueError("No blueprint selected.")

#     headers = {"Authorization": f"Bearer {PRINTIFY_API_KEY}"}
#     async with httpx.AsyncClient() as client:
#         res = await client.get(
#             f"https://api.printify.com/v1/catalog/blueprints/{blueprint['id']}/print_providers.json",
#             headers=headers
#         )
#         res.raise_for_status()
#         providers = res.json()

#     ctx.context["providers"] = providers
#     return {
#         "type": "chat",
#         "role": "assistant",
#         "content": f"Here are the available print providers for {blueprint['title']}:\n" +
#                    "\n".join(f"• {p['title']} (ID: {p['id']})" for p in providers)
#     }

# @function_tool
# async def select_blueprint(ctx: RunContextWrapper[dict], user_reply: str) -> dict:
#     """
#     Matches user's response to a blueprint from previous matches and saves it to product context.
#     """
#     blueprint_matches = ctx.context.get("blueprint_matches", [])
#     user_reply_lower = user_reply.strip().lower()

#     # Try to match by ID or fuzzy title
#     selected = None
#     for bp in blueprint_matches:
#         if user_reply_lower == str(bp["id"]):
#             selected = bp
#             break
#         if user_reply_lower in bp["title"].lower():
#             selected = bp
#             break

#     if not selected:
#         return {
#             "type": "chat",
#             "role": "assistant",
#             "content": "Hmm, I couldn't find that product. Please respond with the name or Blueprint ID of one of the suggestions I gave you."
#         }

#     # Store in context under product
#     ctx.context["product"] = {
#         "blueprint_id": selected["id"],
#         "blueprint_name": selected["title"],
#     }

#     return {
#         "type": "chat",
#         "role": "assistant",
#         "content": f"Great choice! You've selected: {selected['title']} (ID: {selected['id']}). Next, I'll find the best print providers for this product..."
#     }

# @function_tool
# async def get_matching_blueprints(ctx: RunContextWrapper[dict], prompt: str) -> dict:
#     """
#     Fetch Printify blueprints and match against the user prompt to suggest products.
#     """
#     # Step 1: Fetch blueprints
#     headers = {"Authorization": f"Bearer {PRINTIFY_API_KEY}"}
#     async with httpx.AsyncClient() as client:
#         res = await client.get("https://api.printify.com/v1/catalog/blueprints.json", headers=headers)
#         res.raise_for_status()
#         blueprints = res.json()

#     # Step 2: Match based on simple fuzzy matching against title
#     prompt_lower = prompt.lower()
#     matches = [
#         bp for bp in blueprints
#         if any(keyword in prompt_lower for keyword in bp["title"].lower().split())
#     ]

#     # Step 3: Sort matches (basic heuristic: by match count)
#     ranked_matches = sorted(matches, key=lambda b: sum(kw in prompt_lower for kw in b["title"].lower().split()), reverse=True)
#     top_matches = ranked_matches[:5]

#     # Step 4: Store in context for follow-ups
#     ctx.context["blueprint_matches"] = top_matches  # not typed, short-lived cache

#     # Step 5: Build structured message
#     content_lines = ["Based on your description, I found these product options:\n"]
#     for bp in top_matches:
#         content_lines.append(f"• {bp['title']} (Blueprint ID: {bp['id']})")

#     content_lines.append("\nWhich one of these would you like to use? You can reply with the name or Blueprint ID.")
#     return {
#         "type": "chat",
#         "role": "assistant",
#         "content": "\n".join(content_lines)
#     }

# @function_tool
# async def handle_printify_prompt(ctx: RunContextWrapper[dict], input: str) -> dict:
#     ctx.context["last_prompt"] = input
#     blueprint_matches = ctx.context.get("blueprint_matches", [])

#     # Try to parse as int (ID)
#     try:
#         blueprint_id = int(input)
#         return await select_blueprint(ctx, blueprint_id)
#     except ValueError:
#         pass

#     # Try to match name
#     for bp in blueprint_matches:
#         if input.strip().lower() in bp["title"].lower():
#             return await select_blueprint(ctx, input)

#     # If no match, assume it's a fresh product request
#     return await get_matching_blueprints(ctx, input)

# printify_agent = Agent(
#     name="PrintifyAgent",
#     instructions="""
#     You are the PrintifyAgent.

#     When a user describes a product, call `get_matching_blueprints`.

#     If the user replies with a name or blueprint ID from the list, call `select_blueprint`.

#     Never respond manually — always use tools to fetch or select blueprints.
#     """,
#     tools=[handle_printify_prompt, get_matching_blueprints, select_blueprint],
#     model="gpt-4",
#     tool_use_behavior="run_llm_again"
# )


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