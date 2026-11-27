"""
step03_react_agent.py — Wednesday: is the stock expensive versus its peers?
A ReAct agent built with the Claude Agent SDK and three live-data tools.

Run it:
    pip install claude-agent-sdk yfinance python-dotenv
    python step03_react_agent.py
"""
import asyncio
import json
import statistics

import yfinance as yf
from dotenv import load_dotenv
from claude_agent_sdk import (
    AssistantMessage, ClaudeAgentOptions, ClaudeSDKClient, TextBlock,
    ToolResultBlock, ToolUseBlock, UserMessage, create_sdk_mcp_server, tool,
)

load_dotenv()                      # the SDK reads ANTHROPIC_API_KEY from the env


@tool(
    "get_valuation_ratios",                                               # ① name
    "Retrieve valuation ratios (P/E, EV/EBITDA, P/B, PEG) for a given ticker.",  # ② when to use
    {"ticker": str},                                                      # ③ inputs
)
async def get_valuation_ratios(args):
    info = yf.Ticker(args["ticker"]).info              # a big dict of Yahoo fields
    data = {
        "PE": info.get("trailingPE"),
        "EV_EBITDA": info.get("enterpriseToEbitda"),
        "PB": info.get("priceToBook"),
        "PEG": info.get("pegRatio") or info.get("trailingPegRatio"),
    }
    return {"content": [{"type": "text", "text": json.dumps(data)}]}  # ④ MCP format


# A handful of large-cap tickers per sector, used to compute live sector medians.
SECTOR_TICKERS = {
    "Technology": ["MSFT", "NVDA", "GOOGL", "META", "ORCL",
                   "CRM", "ADBE", "AMD", "INTC", "CSCO"],
    "Healthcare": ["JNJ", "UNH", "PFE", "MRK", "ABBV",
                   "TMO", "ABT", "LLY", "BMY", "AMGN"],
    "Financials": ["JPM", "BAC", "WFC", "GS", "MS",
                   "C", "BLK", "AXP", "USB", "PNC"],
}


@tool(
    "get_sector_median_pe",
    "Retrieve the median P/E and EV/EBITDA for a given GICS sector.",
    {"sector": str},
)
async def get_sector_median_pe(args):
    pes, evs = [], []
    for tk in SECTOR_TICKERS.get(args["sector"], []):    # unknown sector → []
        info = yf.Ticker(tk).info
        if info.get("trailingPE"):                        # skip missing values
            pes.append(info["trailingPE"])
        if info.get("enterpriseToEbitda"):
            evs.append(info["enterpriseToEbitda"])
    data = {
        "median_pe": round(statistics.median(pes), 2) if pes else None,
        "median_ev_ebitda": round(statistics.median(evs), 2) if evs else None,
        "sample_size": len(pes),                          # how many names counted
    }
    return {"content": [{"type": "text", "text": json.dumps(data)}]}


@tool(
    "get_balance_sheet",
    "Retrieve balance sheet summary (net cash in $bn, debt-to-equity) for a ticker.",
    {"ticker": str},
)
async def get_balance_sheet(args):
    info = yf.Ticker(args["ticker"]).info
    cash = info.get("totalCash") or 0
    debt = info.get("totalDebt") or 0
    de = info.get("debtToEquity")                         # Yahoo gives 80.0 for 0.8x
    data = {
        "net_cash_bn": round((cash - debt) / 1e9, 1),     # negative = net debt
        "debt_to_equity": round(de / 100, 2) if de else None,
    }
    return {"content": [{"type": "text", "text": json.dumps(data)}]}


SYSTEM_PROMPT = """You are a financial research analyst following the ReAct pattern.
For every step, first emit a 'Thought:' line explaining your plan or
interpretation, then call the appropriate tool. After each observation, briefly
reason about what it means before the next step. Conclude with a clear,
well-grounded recommendation."""


async def run_react_agent(question: str) -> str:
    server = create_sdk_mcp_server(                            # ① a tool "shop"
        name="finance",
        version="1.0.0",
        tools=[get_valuation_ratios, get_sector_median_pe, get_balance_sheet],
    )
    options = ClaudeAgentOptions(                              # ② the agent's rules
        model="claude-sonnet-4-6",
        system_prompt=SYSTEM_PROMPT,
        mcp_servers={"finance": server},
        allowed_tools=[                                        # mcp__<server>__<tool>
            "mcp__finance__get_valuation_ratios",
            "mcp__finance__get_sector_median_pe",
            "mcp__finance__get_balance_sheet",
        ],
    )
    final = ""
    async with ClaudeSDKClient(options=options) as client:    # ③ open the session
        await client.query(question)                           # ④ ask
        async for msg in client.receive_response():            # ⑤ stream every message
            if isinstance(msg, AssistantMessage):              # Claude speaking
                for block in msg.content:
                    if isinstance(block, TextBlock):           # → THOUGHT (or answer)
                        print(f"\n[THOUGHT] {block.text.strip()}")
                        final = block.text
                    elif isinstance(block, ToolUseBlock):      # → ACTION
                        print(f"\n[ACTION] {block.name}({block.input})")
            elif isinstance(msg, UserMessage):                 # tool results come back
                content = msg.content if isinstance(msg.content, list) else []
                for block in content:
                    if isinstance(block, ToolResultBlock):     # → OBSERVATION
                        print(f"[OBSERVATION] {block.content}")
    return final                                               # ⑥ the last text = answer


if __name__ == "__main__":
    question = (
        "Is Apple (AAPL) overvalued relative to the Technology sector? "
        "What does this imply for a long-only portfolio?"
    )
    answer = asyncio.run(run_react_agent(question))
    print("\n" + "=" * 60)
    print("FINAL ANSWER")
    print("=" * 60)
    print(answer)
