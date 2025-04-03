from agents import Agent, function_tool, Runner
from agents.run_context import RunContextWrapper
from design_agent import design_agent

@function_tool
async def handle_user_prompt(ctx: RunContextWrapper[dict], input: str) -> dict:
    """
    Orchestrator tool that delegates prompt to the design agent.
    Expects and returns a structured design message.
    """
    ctx.context["last_prompt"] = input

    result = await Runner.run(design_agent, input, context=ctx.context)

    # The design agent already sets the context, so we don't need to set it again
    return result.final_output

orchestrator_agent = Agent(
    name="OrchestratorAgent",
    instructions="You are an assistant that processes user prompts. When the user requests a design, use the handle_user_prompt tool to generate it. The tool will return a structured design message. You must return this exact message as your response, not as a string or content. The message should be a dictionary with type 'design', not a string representation of a dictionary.",
    tools=[handle_user_prompt],
    model="gpt-4",
    tool_use_behavior="run_llm_again"
)
