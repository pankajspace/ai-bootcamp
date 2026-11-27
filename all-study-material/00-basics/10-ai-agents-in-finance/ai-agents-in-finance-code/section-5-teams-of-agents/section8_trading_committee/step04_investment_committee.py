"""
Section 8 lab — An AI investment committee (LangGraph)
======================================================
Style: deterministic FAN-OUT / FAN-IN with a hierarchical synthesis.

          ┌── fundamentals (Sonnet) ──┐
          ├── technicals   (Sonnet) ──┤
  START ──┤                           ├──► portfolio_manager (Opus) ──► risk_officer ──► END
          ├── sentiment    (Haiku)  ──┤                                 (rules + Opus)
          └── macro        (Sonnet) ──┘

    • Numbers are fetched and computed in PLAIN PYTHON (yfinance + pandas).
    • LLMs only read those numbers and write short reports.
    • The graph itself is the orchestrator: no LLM decides who runs next.

How to run
----------
1. pip install langgraph langchain-anthropic yfinance pandas python-dotenv
2. .env (here or one folder up):   ANTHROPIC_API_KEY=sk-ant-...
3. python step04_investment_committee.py            # TSLA
   python step04_investment_committee.py MSFT

Cost: 6 LLM calls per decision. Live data: fine for TODAY's decision only
(see step05_backtest.py for why that matters). Learning only — not investment advice.
"""

from __future__ import annotations

import re
import sys
from typing import TypedDict

import yfinance as yf
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

load_dotenv()

# One model per cost tier. Change the names here and nowhere else.
# We never pass temperature: newer Claude models no longer accept it.
OPUS_MODEL, SONNET_MODEL, HAIKU_MODEL = "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"
opus = ChatAnthropic(model=OPUS_MODEL, max_tokens=2048)      # PM + risk: hardest reasoning
sonnet = ChatAnthropic(model=SONNET_MODEL, max_tokens=1500)  # three analysts
haiku = ChatAnthropic(model=HAIKU_MODEL, max_tokens=800)     # sentiment: cheap, high volume

SINGLE_NAME_CAP_PCT = 3.0     # firm-wide limit per stock — known to the risk officer ONLY
VOL_CEILING = 0.60            # 60% annualised volatility → automatic veto
MIN_CONFIDENCE = 50

class CommitteeState(TypedDict):
    ticker: str
    indicators: dict            # written by technicals; re-used by the risk officer
    fundamentals_report: str    # ┐
    technicals_report: str      # │ four analysts write four DIFFERENT keys,
    sentiment_report: str       # │ in parallel → no clash, no reducer needed
    macro_report: str           # ┘
    pm_thesis: str
    risk_verdict: str
    final_decision: str

def fetch_fundamentals(ticker: str) -> dict:
    info = yf.Ticker(ticker).info or {}
    keys = ["trailingPE", "forwardPE", "priceToBook", "returnOnEquity", "profitMargins",
            "debtToEquity", "currentRatio", "revenueGrowth", "earningsGrowth"]
    return {k: info.get(k) for k in keys}


def compute_indicators(ticker: str, period: str = "1y") -> dict:
    close = yf.Ticker(ticker).history(period=period)["Close"]
    sma_50 = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else None
    sma_200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else None
    delta = close.diff()                               # day-to-day change
    gain = delta.clip(lower=0).rolling(14).mean()      # average up-move, 14 days
    loss = (-delta.clip(upper=0)).rolling(14).mean()   # average down-move, 14 days
    rsi = (100 - 100 / (1 + gain / loss)).iloc[-1]
    vol_30d = close.pct_change().rolling(30).std().iloc[-1] * (252 ** 0.5)
    return {
        "last_close": round(float(close.iloc[-1]), 2),
        "sma_50": round(float(sma_50), 2) if sma_50 is not None else None,
        "sma_200": round(float(sma_200), 2) if sma_200 is not None else None,
        "rsi_14": round(float(rsi), 1),
        "vol_30d_annualized": round(float(vol_30d), 4),
    }


def fetch_macro_snapshot() -> dict:
    vix = yf.Ticker("^VIX").history(period="5d")["Close"].iloc[-1]
    tnx = yf.Ticker("^TNX").history(period="5d")["Close"].iloc[-1]
    spx = yf.Ticker("^GSPC").history(period="1mo")["Close"]
    return {
        "vix": round(float(vix), 2),
        "us_10y_yield_pct": round(float(tnx), 2),
        "spx_1m_return_pct": round(float((spx.iloc[-1] / spx.iloc[0] - 1) * 100), 2),
    }

GENERIC = {"inc", "inc.", "corp", "corp.", "corporation", "company", "co", "holdings",
           "group", "the", "plc", "ltd", "class", "platforms"}


def _is_about_company(title: str, ticker: str, short_name: str) -> bool:
    """Keep a headline only if it names the ticker or a meaningful word of the company name."""
    words = re.findall(r"[A-Za-z0-9&.]+", title)
    if ticker.upper() in (w.upper().strip(".") for w in words):
        return True
    name_words = [w.lower().strip(",.") for w in short_name.split()]
    key_words = [w for w in name_words if len(w) >= 4 and w not in GENERIC]
    return any(k in title.lower() for k in key_words)


def fetch_news(ticker: str, n: int = 8) -> list[str]:
    """Up to n headlines PRIMARILY about the ticker: '[date, publisher] title — first sentence'."""
    try:
        stock = yf.Ticker(ticker)
        short_name = (stock.info or {}).get("shortName", "")
        items = stock.news or []
    except Exception:
        items, short_name = [], ""
    lines = []
    for it in items:
        content = it.get("content", it)
        title = content.get("title") or it.get("title")
        if not title or not _is_about_company(title, ticker, short_name):
            continue                                   # market-wide noise → skip
        publisher = (content.get("provider") or {}).get("displayName", "")
        pub_date = (content.get("pubDate") or "").split("T", 1)[0]
        summary = (content.get("summary") or content.get("description") or "").strip()
        m = re.search(r"([^.!?]*[.!?])", summary)
        first = m.group(1).strip() if m else summary[:200]
        meta = ", ".join(p for p in (pub_date, publisher) if p)
        line = (f"[{meta}] " if meta else "") + title + (f" — {first}" if first else "")
        lines.append(line)
        if len(lines) >= n:
            break
    return lines

def fundamentals_analyst(state: CommitteeState) -> dict:
    data = fetch_fundamentals(state["ticker"])                       # 1. numbers, in code
    sys_msg = SystemMessage(content=(                                # 2. role + output shape
        "You are a senior equity fundamentals analyst. Given the ratios, write a SHORT "
        "report (max 150 words) covering: (1) valuation stance, (2) profitability, "
        "(3) balance-sheet strength, (4) growth. Conclude with a tilt: "
        "BULLISH / NEUTRAL / BEARISH on fundamentals."))
    msg = HumanMessage(content=f"Ticker: {state['ticker']}\nRatios: {data}")
    out = sonnet.invoke([sys_msg, msg])                              # 3. the right tier
    return {"fundamentals_report": out.content}                      # 4. ONLY my own key


def technicals_analyst(state: CommitteeState) -> dict:
    ind = compute_indicators(state["ticker"])
    sys_msg = SystemMessage(content=(
        "You are a technical analyst. Given price-derived indicators, write a SHORT report "
        "(max 120 words) on trend (price vs SMA50/SMA200), momentum (RSI) and volatility. "
        "Conclude with: BULLISH / NEUTRAL / BEARISH on technicals."))
    msg = HumanMessage(content=f"Ticker: {state['ticker']}\nIndicators: {ind}")
    out = sonnet.invoke([sys_msg, msg])
    return {"technicals_report": out.content, "indicators": ind}     # keep the snapshot


def sentiment_analyst(state: CommitteeState) -> dict:
    headlines = fetch_news(state["ticker"])
    body = "\n- ".join(headlines) if headlines else "(no headlines available)"
    sys_msg = SystemMessage(content=(
        "You are a news sentiment analyst. Each line is one article, already filtered to "
        "be primarily about the ticker, formatted '[date, publisher] title — first sentence'. "
        "Use the metadata, not just the title:\n"
        "- Weight RECENT articles more heavily (sentiment decays).\n"
        "- Treat tier-1 financial press (Reuters, Bloomberg, WSJ, FT) as harder evidence "
        "than opinion outlets or blogs.\n"
        "- If coverage is concentrated in one publisher, flag a possible PR push.\n"
        "Produce a SHORT report (max 120 words) and score sentiment as: "
        "POSITIVE / MIXED / NEGATIVE."))
    msg = HumanMessage(content=f"Ticker: {state['ticker']}\nHeadlines:\n- {body}")
    out = haiku.invoke([sys_msg, msg])
    return {"sentiment_report": out.content}


def macro_analyst(state: CommitteeState) -> dict:
    macro = fetch_macro_snapshot()                    # no ticker: the market regime
    sys_msg = SystemMessage(content=(
        "You are a macro strategist. Given a short macro snapshot, write a SHORT report "
        "(max 120 words) on the regime (risk-on / risk-off / neutral) and what it implies "
        "for a single-name long-only equity position."))
    msg = HumanMessage(content=f"Macro snapshot: {macro}")
    out = sonnet.invoke([sys_msg, msg])
    return {"macro_report": out.content}

PM_LINE_RE = re.compile(
    r"ACTION\s*=\s*(BUY|HOLD|SELL)\s*;\s*CONFIDENCE\s*=\s*(\d+)\s*;\s*SIZE_PCT\s*=\s*([\d.]+)",
    re.IGNORECASE)


def parse_pm_line(thesis: str) -> tuple[str, int, float] | None:
    """Read 'ACTION=BUY; CONFIDENCE=68; SIZE_PCT=2.0' → ('BUY', 68, 2.0). None if missing."""
    matches = PM_LINE_RE.findall(thesis)
    if not matches:
        return None
    action, conf, size = matches[-1]                  # the LAST such line wins
    return action.upper(), int(conf), float(size)


def portfolio_manager(state: CommitteeState) -> dict:
    sys_msg = SystemMessage(content=(
        "You are the Portfolio Manager. Synthesise the four analyst reports into a single "
        "thesis (max 250 words). End STRICTLY with one line of the form:\n"
        "ACTION=<BUY|HOLD|SELL>; CONFIDENCE=<0-100>; SIZE_PCT=<0.0-5.0>\n\n"
        "SIZE_PCT is the target position as % of TOTAL PORTFOLIO NAV. Size purely on your "
        "conviction; do not anticipate any downstream review. Scale:\n"
        "  0.0      -> HOLD or SELL (no new long exposure)\n"
        "  0.5-1.0  -> probe / starter position when conviction is mixed\n"
        "  1.0-2.0  -> standard BUY at moderate conviction (CONFIDENCE 50-70)\n"
        "  2.0-3.0  -> strong BUY at high conviction (CONFIDENCE 70+)\n"
        "  3.1-5.0  -> concentrated bet: only if EVERY analyst is bullish AND macro supports it\n"
        "A BUY at SIZE_PCT=0 is incoherent — pick HOLD instead. "
        "A HOLD or SELL must have SIZE_PCT=0."))
    msg = HumanMessage(content=(
        f"Ticker: {state['ticker']}\n\n"
        f"--- Fundamentals ---\n{state['fundamentals_report']}\n\n"
        f"--- Technicals ---\n{state['technicals_report']}\n\n"
        f"--- Sentiment ---\n{state['sentiment_report']}\n\n"
        f"--- Macro ---\n{state['macro_report']}"))
    out = opus.invoke([sys_msg, msg])
    return {"pm_thesis": out.content}

VERDICT_RE = re.compile(r"VERDICT\s*=\s*(APPROVED|REJECTED)", re.IGNORECASE)


def risk_officer(state: CommitteeState) -> dict:
    vol = state["indicators"]["vol_30d_annualized"]      # the SAME snapshot the analyst saw
    parsed = parse_pm_line(state["pm_thesis"])

    # Layer 1 — hard rules in code. Numbers are compared by Python, never by the LLM.
    problems = []
    if vol > VOL_CEILING:
        problems.append(f"realized 30d vol {vol:.1%} exceeds the {VOL_CEILING:.0%} ceiling")
    if parsed is None:
        problems.append("PM thesis has no valid ACTION/CONFIDENCE/SIZE_PCT line")
    else:
        action, conf, size = parsed
        if action == "BUY" and size > SINGLE_NAME_CAP_PCT:
            problems.append(f"SIZE_PCT {size} is above the {SINGLE_NAME_CAP_PCT}% single-name cap")
        if action == "BUY" and conf < MIN_CONFIDENCE:
            problems.append(f"CONFIDENCE {conf} is below {MIN_CONFIDENCE}")
        if (action == "BUY") != (size > 0):
            problems.append(f"incoherent line: {action} with SIZE_PCT={size}")
    if problems:
        return {"risk_verdict": "VETO: " + "; ".join(problems),
                "final_decision": "HOLD (risk veto)"}

    action = parsed[0]
    if action != "BUY":                                  # nothing to approve: no new risk
        return {"risk_verdict": f"No new long exposure ({action}).", "final_decision": action}

    # Layer 2 — the judgment call an LLM is good at: did the thesis ignore the macro picture?
    sys_msg = SystemMessage(content=(
        "You are the Chief Risk Officer. The numeric limits have ALREADY been checked in code. "
        "Your only job: REJECT if the thesis recommends BUY while ignoring or dismissing "
        "material macro headwinds described in the macro report; otherwise APPROVE. "
        "Reply STRICTLY: VERDICT=<APPROVED|REJECTED>; REASON=<one sentence>"))
    msg = HumanMessage(content=(
        f"Macro report:\n{state['macro_report']}\n\nPM thesis:\n{state['pm_thesis']}"))
    out = opus.invoke([sys_msg, msg])
    m = VERDICT_RE.search(out.content)
    verdict = m.group(1).upper() if m else "REJECTED"   # unreadable answer → fail SAFE
    final = action if verdict == "APPROVED" else "HOLD (risk rejected)"
    return {"risk_verdict": out.content, "final_decision": final}

def build_committee():
    g = StateGraph(CommitteeState)
    g.add_node("fundamentals", fundamentals_analyst)
    g.add_node("technicals", technicals_analyst)
    g.add_node("sentiment", sentiment_analyst)
    g.add_node("macro", macro_analyst)
    g.add_node("portfolio_manager", portfolio_manager)
    g.add_node("risk_officer", risk_officer)
    for analyst in ("fundamentals", "technicals", "sentiment", "macro"):
        g.add_edge(START, analyst)                 # fan-out: all four start together
        g.add_edge(analyst, "portfolio_manager")   # fan-in: PM waits for all four
    g.add_edge("portfolio_manager", "risk_officer")
    g.add_edge("risk_officer", END)
    return g.compile()


COMMITTEE = build_committee()                      # compile once, reuse for every ticker


def run_committee(ticker: str) -> dict:
    initial: CommitteeState = {
        "ticker": ticker.upper(), "indicators": {},
        "fundamentals_report": "", "technicals_report": "",
        "sentiment_report": "", "macro_report": "",
        "pm_thesis": "", "risk_verdict": "", "final_decision": "",
    }
    return COMMITTEE.invoke(initial)

if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "TSLA"
    result = run_committee(ticker)
    print("=" * 80)
    print(f"FINAL DECISION for {ticker.upper()}: {result['final_decision']}")
    print("=" * 80)
    print("--- PM thesis ---\n" + result["pm_thesis"])
    print("\n--- Risk verdict ---\n" + result["risk_verdict"])
