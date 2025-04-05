from agents import Agent, function_tool, Runner
from agents.run_context import RunContextWrapper
from design_agent import design_agent
from printify_agent import printify_agent

@function_tool
async def handle_user_prompt(ctx: RunContextWrapper[dict], input: str) -> dict:
    ctx.context["last_prompt"] = input
    # TODO: introduct delegation logic for using design agent later
    result = await Runner.run(printify_agent, input, context=ctx.context)
    # result = await Runner.run(design_agent, input, context=ctx.context)

    return result.final_output


orchestrator_agent = Agent(
    name="OrchestratorAgent",
    instructions=(
      """
      You are the OrchestratorAgent.

      You handle user prompts and delegate them to other agents. For now, all input must be sent to the PrintifyAgent.

      Always call the `handle_user_prompt` tool. Do not try to answer the prompt yourself.
      """
    ),
    tools=[handle_user_prompt],
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
# - Later this (handle_user_prompt) will become LLM classification logic, but for now this is totally serviceable.


# ------------------------------------------------------------
#  Old Working Base Tool
# ------------------------------------------------------------

# @function_tool
# async def handle_user_prompt(ctx: RunContextWrapper[dict], input: str) -> dict:
#     """
#     Orchestrator tool that delegates prompt to the design agent.
#     Expects and returns a structured design message.
#     """
#     ctx.context["last_prompt"] = input

#     result = await Runner.run(design_agent, input, context=ctx.context)

#     # The design agent already sets the context, so we don't need to set it again
#     return result.final_output