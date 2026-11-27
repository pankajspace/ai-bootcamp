"""Lab 2A · A ratio tool: the agent fetches liquidity ratios with FinanceToolkit."""
import asyncio

import pandas as pd
from agents import Agent, Runner, function_tool

from fundamentals_tool import (LIQUIDITY_RATIOS, PROFITABILITY_RATIOS, VALUATION_RATIOS,
                               collect_ratios, pick)


# Step 2 · the tool: fetch everything, keep only what we need (our three "shopping lists")
@function_tool
def get_company_fundamentals(ticker: str) -> dict[str, pd.DataFrame]:
    """Get profitability, valuation and liquidity ratios for a given ticker."""
    ratios = collect_ratios(ticker)
    return {
        "profitability_ratios": pick(ratios, PROFITABILITY_RATIOS),
        "valuation_ratios":     pick(ratios, VALUATION_RATIOS),
        "liquidity_ratios":     pick(ratios, LIQUIDITY_RATIOS),
    }


# Step 3 · the agent and the question
fundamental_retrieval_agent = Agent(
    name="Fundamental Retrieval Agent",
    model="gpt-4o-mini",
    instructions="""
You are a Fundamental Retrieval Agent.
Tasks:
1) Call the fundamentals tool for the specified ticker.
2) Output the desired set of ratios.
""",
    tools=[get_company_fundamentals],
)


async def main():
    fundamental_results = await Runner.run(fundamental_retrieval_agent, """Proceed step by step:
1- List 3 liquidity ratios and explain their significance.
2- Provide Apple's values for the three listed liquidity ratios for the most
recent fiscal year, knowing that we are in 2026.
""")
    print(fundamental_results.final_output)


if __name__ == "__main__":
    asyncio.run(main())
