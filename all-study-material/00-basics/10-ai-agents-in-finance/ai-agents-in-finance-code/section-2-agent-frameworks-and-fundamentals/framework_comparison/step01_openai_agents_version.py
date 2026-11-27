"""OpenAI Agents SDK: one agent, two tools, a runner (≈2,651 tokens in the notes' run)."""
from agents import Agent, Runner, function_tool

from common import MODEL, compute_pe_ratio, get_stock_data, input_message, system_message

agent = Agent(
    name="Financial Analysis Agent",
    instructions=system_message,
    tools=[function_tool(get_stock_data), function_tool(compute_pe_ratio)],
    model=MODEL,
)
result = Runner.run_sync(agent, input_message)
print(result.final_output)                 # a prose memo; steps appear in OpenAI tracing
