import os
import requests
from dotenv import load_dotenv
from agents import Agent, function_tool, RunContextWrapper
from tenacity import retry, stop_after_attempt, wait_exponential
from cachetools import TTLCache

load_dotenv()

PRINTIFY_API_KEY = os.getenv("PRINTIFY_API_KEY")
if not PRINTIFY_API_KEY:
    raise ValueError("PRINTIFY_API_KEY is not set in .env")

printify_shop_id = os.getenv("PRINTIFY_SHOP_ID")
if not printify_shop_id:
    raise ValueError("PRINTIFY_SHOP_ID is not set in .env")

# Cache for blueprints (1-hour TTL)
blueprints_cache = TTLCache(maxsize=1, ttl=3600)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_printify_data(url: str, headers: dict) -> dict:
    """Fetch data from Printify API with retry logic."""
    response = requests.get(url, headers=headers)
    if response.status_code == 429:
        raise Exception("Rate limit exceeded")
    response.raise_for_status()
    return response.json()

def summarize_list(items: list, key: str, max_items: int = 5) -> str:
    """Summarize a list for token efficiency."""
    if len(items) > max_items:
        return f"{len(items)} items available. First {max_items}: " + ", ".join(item[key] for item in items[:max_items])
    return ", ".join(item[key] for item in items)

@function_tool
async def select_variants(context: RunContextWrapper[dict], selection: str) -> dict:
    """
    Handles the user's variant selection and stores it in the context.
    
    Args:
        context: The run context wrapper.
        selection: User input for variant selection.
    
    Returns:
        Dict with type 'printify' and selection result.
    """
    print("select_variants called with selection:", selection)
    if not context.context.get("awaiting_variant_selection", False):
        return {"type": "printify", "message": "No variant selection is currently awaited."}
    
    try:
        index = int(selection.split()[-1]) - 1
        selected_variant = context.context["variants_list"][index]
        context.context["selected_variant"] = selected_variant
        context.context["awaiting_variant_selection"] = False
        return {"type": "printify", "message": f"You have selected variant: {selected_variant['title']}"}
    except (IndexError, ValueError):
        return {"type": "printify", "message": "Invalid selection. Please try again with a valid number."}

@function_tool
async def get_variants(context: RunContextWrapper[dict]) -> dict:
    """
    Fetches variants for the selected blueprint and print provider from the context.
    
    Args:
        context: The run context wrapper.
    
    Returns:
        Dict with type 'printify' and variant options.
    """
    print("get_variants called with context")
    if "selected_blueprint" not in context.context or "selected_print_provider" not in context.context:
        return {"type": "printify", "message": "Please select a blueprint and print provider first."}
    
    blueprint_id = context.context["selected_blueprint"]["id"]
    print_provider_id = context.context["selected_print_provider"]["id"]
    url = f"https://api.printify.com/v1/catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/variants.json"
    headers = {"Authorization": f"Bearer {PRINTIFY_API_KEY}"}
    try:
        variants = fetch_printify_data(url, headers)
        variant_names = [v["title"] for v in variants]
        context.context["variants_list"] = variants
        context.context["awaiting_variant_selection"] = True
        # Use summarize_list to create a concise message
        summarized_message = summarize_list(variants, "title")
        selection_message = (
            f"Here are the available variants:\n{summarized_message}\n"
            "Please select one by saying 'Select variant X' where X is the number."
        )
        return {"type": "printify", "message": selection_message, "variants": variant_names}
    except Exception as e:
        return {"type": "printify", "message": f"Failed to fetch variants: {str(e)}"}
    
@function_tool
async def select_print_provider(context: RunContextWrapper[dict], selection: str) -> dict:
    """
    Handles the user's print provider selection and stores it in the context.
    
    Args:
        context: The run context wrapper.
        selection: User input for print provider selection.
    
    Returns:
        Dict with type 'printify' and selection result.
    """
    print("select_print_provider called with selection:", selection)
    if not context.context.get("awaiting_print_provider_selection", False):
        return {"type": "printify", "message": "No print provider selection is currently awaited."}
    
    try:
        index = int(selection.split()[-1]) - 1
        selected_pp = context.context["print_providers_list"][index]
        context.context["selected_print_provider"] = selected_pp
        context.context["awaiting_print_provider_selection"] = False
        return {"type": "printify", "message": f"You have selected print provider: {selected_pp['title']}"}
    except (IndexError, ValueError):
        return {"type": "printify", "message": "Invalid selection. Please try again with a valid number."}
    
@function_tool
async def get_print_providers(context: RunContextWrapper[dict]) -> dict:
    """
    Fetches print providers for the selected blueprint from the context.
    
    Args:
        context: The run context wrapper.
    
    Returns:
        Dict with type 'printify' and print provider options.
    """
    print("get_print_providers called with context")
    if "selected_blueprint" not in context.context:
        return {"type": "printify", "message": "No blueprint selected. Please select a blueprint first."}
    
    blueprint_id = context.context["selected_blueprint"]["id"]
    url = f"https://api.printify.com/v1/catalog/blueprints/{blueprint_id}/print_providers.json"
    headers = {"Authorization": f"Bearer {PRINTIFY_API_KEY}"}
    try:
        print_providers = fetch_printify_data(url, headers)
        print_provider_names = [pp["title"] for pp in print_providers]
        context.context["print_providers_list"] = print_providers
        context.context["awaiting_print_provider_selection"] = True
        # Use summarize_list to create a concise message
        summarized_message = summarize_list(print_providers, "title")
        selection_message = (
            f"Here are the available print providers:\n{summarized_message}\n"
            "Please select one by saying 'Select print provider X' where X is the number."
        )
        return {"type": "printify", "message": selection_message, "printProviders": print_provider_names}
    except Exception as e:
        return {"type": "printify", "message": f"Failed to fetch print providers: {str(e)}"}
    
@function_tool
async def select_blueprint(context: RunContextWrapper[dict], selection: str) -> dict:
    """
    Handles the user's blueprint selection and stores it in the context.
    
    Args:
        context: The run context wrapper.
        selection: User input for blueprint selection.
    
    Returns:
        Dict with type 'printify' and selection result.
    """
    print("select_blueprint called with selection:", selection)
    if not context.context.get("awaiting_selection", False):
        return {"type": "printify", "message": "No selection is currently awaited."}
    
    try:
        index = int(selection.split()[-1]) - 1
        selected_bp = context.context["blueprints_list"][index]
        context.context["selected_blueprint"] = selected_bp
        context.context["awaiting_selection"] = False
        return {"type": "printify", "message": f"You have selected: {selected_bp['title']}"}
    except (IndexError, ValueError):
        return {"type": "printify", "message": "Invalid selection. Please try again."}

@function_tool
async def get_blueprints(context: RunContextWrapper[dict], prompt: str) -> dict:
    """
    Fetches Printify blueprints, filters them based on the prompt, and prepares for selection.
    
    Args:
        context: The run context wrapper.
        prompt: User input to filter blueprints.
    
    Returns:
        Dict with type 'printify' and blueprint options.
    """
    print("get_blueprints called with prompt:", prompt)
    url = "https://api.printify.com/v1/catalog/blueprints.json"
    headers = {"Authorization": f"Bearer {PRINTIFY_API_KEY}"}
    try:
        # Use cached data if available
        if "blueprints" not in blueprints_cache:
            blueprints_cache["blueprints"] = fetch_printify_data(url, headers)
        blueprints = blueprints_cache["blueprints"]
        
        # TODO: Improve description to matching catalog blueprints
        keywords = prompt.lower().split()
        matched_blueprints = [bp for bp in blueprints if any(kw in bp["title"].lower() for kw in keywords)]

        if not matched_blueprints:
            return {"type": "printify", "message": "No matching blueprints found"}
        
        context.context["blueprints_list"] = matched_blueprints
        context.context["awaiting_selection"] = True
        blueprint_names = [bp["title"] for bp in matched_blueprints]

        # Use summarize_list to create a concise message
        summarized_message = summarize_list(matched_blueprints, "title")
        selection_message = (
            f"Here are the matching blueprints:\n{summarized_message}\n"
            "Please select one by saying 'Select blueprint X' where X is the number."
        )
        return {"type": "printify", "message": selection_message, "blueprints": blueprint_names}
    except Exception as e:
        print("API call failed:", str(e))
        return {"type": "printify", "message": f"Failed to fetch blueprints: {str(e)}"}

printify_agent = Agent(
    name="PrintifyProductAgent",
    instructions=(
        """
        You are a Printify assistant. Follow these steps strictly:

        1. When the user asks for products or blueprints (e.g., "I want a coffee mug"), use get_blueprints and return its result directly.
        2. Wait for the user to say "Select blueprint X". Then use select_blueprint and return its result directly.
        3. After a blueprint is selected, use get_print_providers and return its result directly.
        4. Wait for the user to say "Select print provider Y". Then use select_print_provider and return its result directly.
        5. After a print provider is selected, use get_variants and return its result directly.
        6. Wait for the user to say "Select variant Z". Then use select_variants and return its result directly.

        Do not call any tool unless the user has provided the necessary input as specified. Do not rephrase tool outputs. Return them as-is with "type": "printify".
        """
    ),
    tools=[get_blueprints, select_blueprint, get_print_providers, select_print_provider, get_variants, select_variants],
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
# - Improve description to matching catalog blueprints
