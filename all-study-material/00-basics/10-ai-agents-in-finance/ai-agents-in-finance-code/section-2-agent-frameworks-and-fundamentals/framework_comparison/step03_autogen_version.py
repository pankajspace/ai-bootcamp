"""AutoGen: even one analyst runs as a "meeting" (≈27,948 tokens in the notes' run)."""
import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient

from common import MODEL, compute_pe_ratio, get_stock_data, input_message, system_message

get_stock_data_tool = FunctionTool(get_stock_data, description=get_stock_data.__doc__)
compute_pe_tool = FunctionTool(compute_pe_ratio, description=compute_pe_ratio.__doc__)

analyst_agent = AssistantAgent(
    name="FinancialAnalyst",
    model_client=OpenAIChatCompletionClient(model=MODEL),
    tools=[get_stock_data_tool, compute_pe_tool],
    system_message=system_message,
)


async def main():
    team = RoundRobinGroupChat(
        participants=[analyst_agent],                      # a meeting with one member
        termination_condition=MaxMessageTermination(10),   # end the meeting after 10 messages
    )
    result = await team.run(task=input_message)
    print(result.messages[-1].content)

asyncio.run(main())
