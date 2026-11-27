"""LangChain 1.0 create_agent, which runs on LangGraph (≈2,805 tokens in the notes' run)."""
from langchain.agents import create_agent

from common import MODEL, compute_pe_ratio, get_stock_data, input_message, system_message

agent = create_agent(
    model=f"openai:{MODEL}",
    tools=[get_stock_data, compute_pe_ratio],
    system_prompt=system_message,
)
output = agent.invoke({"messages": [{"role": "user", "content": input_message}]})
print(output["messages"][-1].content)     # last message = the memo
