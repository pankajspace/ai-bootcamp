"""
Section 7 lab — Multi-agent financial health analyzer
=====================================================
Style: SEQUENTIAL PIPELINE with SHARED STATE and EXPLICIT HANDOFFS
       (built with LlamaIndex AgentWorkflow)

    FundamentalAgent → ProfitabilityAgent → LiquidityAgent → SupervisorAgent

    • Tools do the deterministic work (fetch numbers, compare with thresholds).
    • Agents (LLMs) do the judgment (score 1–10, explain, write the report).
    • Everyone reads/writes one shared "state" dict that lives in ctx.store.

How to run
----------
1. pip install llama-index-core llama-index-llms-openai yfinance python-dotenv
2. Put your key in a .env file (in this folder or the folder above):
       OPENAI_API_KEY=sk-...
3. python step01_health_analyzer.py            # analyses AAPL
   python step01_health_analyzer.py MSFT       # any ticker
   python step01_health_analyzer.py JPM        # a bank: watch the rubric warning!

Cost: one run ≈ 10–14 LLM calls on MODEL (a few cents).
Data: yfinance (free, no key). For learning only — not investment advice.
"""

import asyncio
import sys

import yfinance as yf
from dotenv import load_dotenv
from llama_index.core.agent.workflow import (
    AgentStream,
    AgentWorkflow,
    FunctionAgent,
    ToolCall,
)
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI

load_dotenv()                      # reads OPENAI_API_KEY from .env
MODEL = "gpt-4o"                   # any tool-calling OpenAI model works — change one line
llm = OpenAI(model=MODEL)

# Each rule: (metric label, how to read the number, function that returns a band)
# Bands are decided by CODE, so every run gives the same band for the same number.
def band_profitability(name: str, pct: float) -> str:
    """ROA / ROE / margins, given in percent (26.1 means 26.1%)."""
    limits = {                      # (strong above, weak below)
        "roa": (5, 2),
        "roe": (15, 8),
        "net_margin": (10, 5),
        "gross_margin": (40, 20),
    }
    strong, weak = limits[name]
    if pct > strong:
        return "strong"
    if pct < weak:
        return "weak"
    return "moderate"


def band_liquidity(name: str, x: float) -> str:
    """Current ratio, quick ratio, debt-to-equity and interest coverage (plain ratios)."""
    if name == "current_ratio":
        if x < 1.0:
            return "warning (below 1.0)"
        if x < 1.5:
            return "moderate"
        if x <= 3.0:
            return "healthy"
        return "healthy, but maybe idle cash (above 3.0)"
    if name == "quick_ratio":
        return "healthy" if x > 1.0 else "caution (below 1.0)"
    if name == "debt_to_equity":
        if x > 2.0:
            return "high leverage (above 2.0)"
        if x > 1.5:
            return "moderate"
        if x >= 0.3:
            return "healthy"
        return "conservative (below 0.3)"
    if name == "interest_coverage":
        if x > 3.0:
            return "healthy"
        if x >= 1.5:
            return "moderate"
        return "distress risk (below 1.5)"
    raise ValueError(name)

def fetch_ratios(ticker: str) -> dict:
    """Plain Python, no LLM: pull the raw numbers from Yahoo Finance."""
    t = yf.Ticker(ticker)
    info = t.info or {}

    def pct(key):                   # 0.2613 → 26.13 (percent)
        v = info.get(key)
        return round(v * 100, 2) if v is not None else None

    d_e = info.get("debtToEquity")  # Yahoo gives 151.9 meaning 1.519×
    ratios = {
        "roa": pct("returnOnAssets"),
        "roe": pct("returnOnEquity"),
        "net_margin": pct("profitMargins"),
        "gross_margin": pct("grossMargins"),
        "current_ratio": info.get("currentRatio"),
        "quick_ratio": info.get("quickRatio"),
        "debt_to_equity": round(d_e / 100, 2) if d_e is not None else None,
        "interest_coverage": None,
    }
    try:                            # EBIT ÷ interest expense, latest fiscal year
        inc = t.income_stmt
        ebit = inc.loc["EBIT"].iloc[0]
        interest = abs(inc.loc["Interest Expense"].iloc[0])
        if interest:
            ratios["interest_coverage"] = round(float(ebit / interest), 2)
    except Exception:
        pass                        # some companies don't report it → stays None
    return {"sector": info.get("sector", "Unknown"), "ratios": ratios}

async def get_fundamentals(ctx: Context, ticker: str) -> str:
    """Collect the raw financial ratios for a ticker and save them in shared state."""
    data = await asyncio.to_thread(fetch_ratios, ticker)   # don't block the event loop

    state = await ctx.store.get("state")                    # 1. read the whiteboard
    state["ticker"] = ticker.upper()                        # 2. write my slots
    state["sector"] = data["sector"]
    state["ratios"] = data["ratios"]
    if data["sector"] == "Financial Services":              # banks need CET1 / LCR instead
        state["rubric_warning"] = (
            "Bank or financial firm: current ratio and debt-to-equity do not fit. "
            "Treat the liquidity scores as low-confidence."
        )
    await ctx.store.set("state", state)                     # 3. save it back
    return f"Ratios saved for {ticker.upper()} (sector: {data['sector']})."


async def get_profitability_ratios(ctx: Context) -> str:
    """Read ROA, ROE and margins from shared state and band them against the thresholds."""
    state = await ctx.store.get("state")
    rows = {}
    for name in ("roa", "roe", "net_margin", "gross_margin"):
        v = state["ratios"].get(name)
        rows[name] = {"value_pct": v,
                      "band": band_profitability(name, v) if v is not None else "missing"}
    state["profitability"] = rows
    await ctx.store.set("state", state)
    return str(rows)


async def get_liquidity_ratios(ctx: Context) -> str:
    """Read the liquidity and leverage ratios from shared state and band them."""
    state = await ctx.store.get("state")
    rows = {}
    for name in ("current_ratio", "quick_ratio", "debt_to_equity", "interest_coverage"):
        v = state["ratios"].get(name)
        rows[name] = {"value": v,
                      "band": band_liquidity(name, v) if v is not None else "missing"}
    state["liquidity"] = rows
    await ctx.store.set("state", state)
    warning = state.get("rubric_warning")
    return str(rows) + (f"\nWARNING: {warning}" if warning else "")

SCORING_RULES = (
    "Score EVERY metric from 1 to 10 and justify each score in one sentence using "
    "the actual number. Use the band from the tool as your anchor: "
    "strong/healthy = 8-10, moderate = 5-7, weak/warning/distress = 1-4. "
    "If a value is missing, say so and do not invent it."
)

fundamental_agent = FunctionAgent(
    name="FundamentalAgent",
    description="Collects the raw financial ratios for the ticker.",
    system_prompt=(
        "You are the fundamental data analyst. Call get_fundamentals EXACTLY ONCE "
        "for the ticker in the user's request, then hand off to ProfitabilityAgent."
    ),
    llm=llm,
    tools=[get_fundamentals],
    can_handoff_to=["ProfitabilityAgent"],
)

profitability_agent = FunctionAgent(
    name="ProfitabilityAgent",
    description="Scores profitability: ROA, ROE, net margin, gross margin.",
    system_prompt=(
        "You are the profitability analyst. Call get_profitability_ratios EXACTLY ONCE. "
        + SCORING_RULES + " Then hand off to LiquidityAgent."
    ),
    llm=llm,
    tools=[get_profitability_ratios],
    can_handoff_to=["LiquidityAgent"],
)

liquidity_agent = FunctionAgent(
    name="LiquidityAgent",
    description="Scores liquidity and leverage: current, quick, D/E, interest coverage.",
    system_prompt=(
        "You are the liquidity and solvency analyst. Call get_liquidity_ratios EXACTLY ONCE. "
        + SCORING_RULES + " If the tool returns a WARNING, repeat it. "
        "Then hand off to SupervisorAgent."
    ),
    llm=llm,
    tools=[get_liquidity_ratios],
    can_handoff_to=["SupervisorAgent"],
)

supervisor_agent = FunctionAgent(
    name="SupervisorAgent",
    description="Writes the final financial health report.",
    system_prompt=(
        "You are the head of research. Using the analysts' scores above, write the final "
        "report: (1) profitability summary, (2) liquidity summary, (3) overall health "
        "score 1-10 that is consistent with the individual scores, (4) the two biggest "
        "strengths and the two biggest concerns. If there is a rubric WARNING, put it at "
        "the top. You are the last agent: write the answer yourself, do not hand off."
    ),
    llm=llm,
    tools=[],
    can_handoff_to=[],               # [] = nobody. Leaving it out would allow ANY agent!
)

def build_workflow() -> AgentWorkflow:
    return AgentWorkflow(
        agents=[fundamental_agent, profitability_agent, liquidity_agent, supervisor_agent],
        root_agent=fundamental_agent.name,          # who receives the user's message
        initial_state={                             # the shared whiteboard, empty at start
            "ticker": "",
            "sector": "",
            "ratios": {},
            "profitability": {},
            "liquidity": {},
            "rubric_warning": None,
        },
    )

async def run_analysis(ticker: str, verbose: bool = True) -> dict:
    """Run the 4-agent pipeline once. Returns the report, the final state and the handoffs."""
    handler = build_workflow().run(
        user_msg=f"Provide the financial health analysis of {ticker}.",
        max_iterations=60,                          # default 20 is too tight for 4 agents
    )
    handoffs, last_agent = [], None
    async for event in handler.stream_events():
        if isinstance(event, ToolCall) and event.tool_name == "handoff":
            hop = (last_agent, event.tool_kwargs.get("to_agent"), event.tool_kwargs.get("reason"))
            handoffs.append(hop)                    # audit trail: who, to whom, WHY
            if verbose:
                print(f"\n   🔀 handoff {hop[0]} → {hop[1]}  (reason: {hop[2]})")
        elif isinstance(event, AgentStream):
            if event.current_agent_name != last_agent:
                last_agent = event.current_agent_name
                if verbose:
                    print(f"\n{'=' * 60}\n🤖 Active agent: {last_agent}\n{'=' * 60}")
            if verbose and event.delta:
                print(event.delta, end="", flush=True)

    result = await handler                          # the last agent's answer
    state = await handler.ctx.store.get("state")    # the whiteboard after the run
    return {"ticker": ticker.upper(), "report": str(result), "state": state, "handoffs": handoffs}


if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    out = asyncio.run(run_analysis(ticker))
    print("\n\n--- Deterministic bands saved in shared state ---")
    for section in ("profitability", "liquidity"):
        for metric, row in out["state"][section].items():
            print(f"{section:13} {metric:18} {row}")
