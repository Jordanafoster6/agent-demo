from agents import Agent, function_tool, Runner
from agents.run_context import RunContextWrapper
from design_agent import design_agent
from printify_agent import printify_agent

@function_tool
async def handle_user_prompt(context: RunContextWrapper[dict], input: str) -> dict:
    """Delegates design-related prompts to the design agent."""
    context.context["last_prompt"] = input
    result = await Runner.run(design_agent, input, context=context.context)
    return result.final_output

@function_tool
async def handle_printify_prompt(context: RunContextWrapper[dict], input: str) -> dict:
    """Routes Printify-related prompts to the Printify Product Agent."""
    context.context["last_prompt"] = input
    result = await Runner.run(printify_agent, input, context=context.context)
    return result.final_output

orchestrator_agent = Agent(
    name="OrchestratorAgent",
    instructions=(
        """
        You are an assistant that processes user prompts.
        - Use handle_user_prompt for design requests (e.g., "Create an image of a cat").
        - Use handle_printify_prompt for Printify product, blueprint, or store-related requests (e.g., "I want a coffee mug").
        Return tool outputs as-is without modification.
        """
    ),
    tools=[handle_user_prompt, handle_printify_prompt],
    model="gpt-4",
    tool_use_behavior="run_llm_again"
)


# ------------------------------------------------------------
#  Improvements
# ------------------------------------------------------------

# Introduce delegation logic for using design agent vs printify agent
# Update (handle_user_prompt) from being serviceable to LLM classification logic
