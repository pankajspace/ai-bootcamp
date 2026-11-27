"""Lab 2F · Prompt chaining: retrieval → analysis → BUY / HOLD / SELL, each with a JSON contract."""
import asyncio
import json

import pandas as pd
from agents import Agent, Runner, function_tool

from fundamentals_tool import PROFITABILITY_RATIOS, VALUATION_RATIOS, collect_ratios, pick


# Step 1 · the tool: only profitability and valuation, to keep the context small and focused
@function_tool
def get_company_fundamentals(ticker: str) -> dict[str, pd.DataFrame]:
    """Get the profitability and valuation fundamental ratios for a given ticker."""
    ratios = collect_ratios(ticker)
    return {
        "profitability_ratios": pick(ratios, PROFITABILITY_RATIOS),
        "valuation_ratios":     pick(ratios, VALUATION_RATIOS),
    }


# Step 2 · three agents, each with a JSON contract
MODEL = "gpt-4o-mini"

fundamental_retrieval_agent = Agent(
    name="Fundamental Retrieval Agent", model=MODEL, tools=[get_company_fundamentals],
    instructions="""
You are the Fundamental Retrieval Agent.
Tasks:
1) Call the fundamentals tool for the specified ticker.
2) Output ONLY valid JSON with this schema. Keep the output strictly factual: no interpretation.
{ "ticker": "...", "fundamentals": { ... } }   // raw numbers from tools
""",
)

fundamental_analysis_agent = Agent(
    name="Fundamental Analysis Agent", model=MODEL,
    instructions="""
You are the Fundamental Analysis Agent.
Input: JSON from the Retrieval Agent.
Tasks:
1) Interpret the fundamentals along 2 dimensions:
   - Profitability (profitability, margins, ROE)
   - Valuation (P/E, EV/Sales)
2) Identify 2-3 key risks (e.g., valuation risk, margin sustainability).
3) Output ONLY valid JSON with this schema:
{
  "ticker": "...",
  "fundamentals": { ... },          // keep from input
  "analysis": {
    "Profitability": { "rating": "strong|neutral|weak", "evidence": [string, ...] },
    "valuation": { "rating": "cheap|fair|expensive", "evidence": [string, ...] },
    "risks": [string, ...]
  }
}
Rules:
- Keep evidence short and specific.
""",
)

decision_agent = Agent(
    name="Decision Agent", model=MODEL,
    instructions="""
You are the Decision Agent.
Input: JSON from the Fundamental Analysis Agent.
Tasks: Based only on the input coming from the Fundamental Analysis Agent:
1) Produce a simple stance: BUY, HOLD, or SELL.
2) Provide 3 bullet reasons grounded in the analysis.
3) Provide a "watchlist" section: what metrics would change your stance.
Output ONLY valid JSON:
{ "ticker": "...", "stance": "BUY|HOLD|SELL",
  "summary": { "reasons": [string, string, string], "watchlist": [string, string, string] } }
""",
)


async def main():
    # Step 3 · the whole orchestration is three lines
    fundamental_results  = await Runner.run(fundamental_retrieval_agent, "Provide Apple fundamentals")
    fundamental_analysis = await Runner.run(fundamental_analysis_agent, fundamental_results.final_output)
    final_decision       = await Runner.run(decision_agent, fundamental_analysis.final_output)
    print(final_decision.final_output)

    # Optional add-on · a task guardrail on the final baton
    decision = json.loads(final_decision.final_output)            # crashes here = the agent broke the JSON contract
    assert decision["stance"] in {"BUY", "HOLD", "SELL"}, "Unexpected stance!"
    assert len(decision["summary"]["watchlist"]) == 3, "Watchlist must have 3 items"


if __name__ == "__main__":
    asyncio.run(main())
