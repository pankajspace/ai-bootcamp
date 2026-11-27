"""
Section 8 lab — Stress-test the committee with an adversarial debate (LangGraph)
===============================================================================
Stage 1: the investment committee (step04_investment_committee.py) produces a thesis + decision.
Stage 2: this graph attacks it from both sides, then a judge decides.

          ┌── bull (Claude Opus) ──┐
  START ──┤                        ├──► devil's advocate (Sonnet) ──► judge (Sonnet) ──► END
          └── bear (OpenAI GPT)  ──┘

    • Bull and bear run in PARALLEL and never see each other's argument.
    • Different model families for bull and bear → less "correlated reasoning".
    • The judge may disagree with the committee — and is told so.

How to run
----------
1. pip install langgraph langchain-anthropic langchain-openai yfinance pandas python-dotenv
2. .env:  ANTHROPIC_API_KEY=sk-ant-...   and   OPENAI_API_KEY=sk-...
3. python step06_adversarial_debate.py          # TSLA
   python step06_adversarial_debate.py NVDA

Cost: 6 committee calls + 4 debate calls = 10 LLM calls. Learning only — not advice.
"""

from __future__ import annotations

import re
import sys
from typing import TypedDict

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from step04_investment_committee import OPUS_MODEL, SONNET_MODEL, run_committee

load_dotenv()
BEAR_MODEL = "gpt-4o"                       # a DIFFERENT model family on purpose

bull_model = ChatAnthropic(model=OPUS_MODEL, max_tokens=1500)
bear_model = ChatOpenAI(model=BEAR_MODEL, max_tokens=1500)
devil_model = ChatAnthropic(model=SONNET_MODEL, max_tokens=1000)
judge_model = ChatAnthropic(model=SONNET_MODEL, max_tokens=1500)


class DebateState(TypedDict):
    ticker: str
    committee_thesis: str       # ← copied in from stage 1
    committee_decision: str     # ← copied in from stage 1
    bull_case: str
    bear_case: str
    devil_critique: str
    judge_verdict: str
    final_decision: str

def _case_message(state: DebateState) -> HumanMessage:
    return HumanMessage(content=(
        f"Ticker: {state['ticker']}\n"
        f"Committee thesis:\n{state['committee_thesis']}\n"
        f"Committee decision: {state['committee_decision']}"))


def bull_node(state: DebateState) -> dict:
    sys_msg = SystemMessage(content=(
        "You are a BULL analyst. Construct the strongest possible case to ENTER a long "
        "position. Cite the strongest evidence from the committee thesis: catalysts, "
        "valuation support, technical confirmation, sentiment tailwinds. Be concrete and "
        "do NOT hedge. Max 200 words. End with: BULL_CONVICTION=<0-100>."))
    return {"bull_case": bull_model.invoke([sys_msg, _case_message(state)]).content}


def bear_node(state: DebateState) -> dict:
    sys_msg = SystemMessage(content=(
        "You are a BEAR analyst. Construct the strongest possible case AGAINST entering a "
        "long position. Surface risks the committee may have under-weighted: tail risks, "
        "macro headwinds, valuation stretch, sentiment crowding, technical exhaustion. Be "
        "concrete and do NOT hedge. Max 200 words. End with: BEAR_CONVICTION=<0-100>."))
    return {"bear_case": bear_model.invoke([sys_msg, _case_message(state)]).content}

def devil_advocate(state: DebateState) -> dict:
    sys_msg = SystemMessage(content=(
        "You are a Devil's Advocate. Identify the SINGLE weakest claim in the BULL case and "
        "the SINGLE weakest claim in the BEAR case, and explain in one sentence each why "
        "those claims are weak. Max 150 words."))
    msg = HumanMessage(content=f"BULL case:\n{state['bull_case']}\n\nBEAR case:\n{state['bear_case']}")
    return {"devil_critique": devil_model.invoke([sys_msg, msg]).content}

VERDICT_RE = re.compile(r"VERDICT\s*=\s*(BUY|HOLD|SELL)", re.IGNORECASE)


def _parse_verdict(text: str) -> str:
    m = VERDICT_RE.search(text)
    return m.group(1).upper() if m else "HOLD"   # unreadable → the safe default


def judge_node(state: DebateState) -> dict:
    sys_msg = SystemMessage(content=(
        "You are a NEUTRAL Judge. Weigh the bull case, the bear case and the devil's "
        "critique. Issue a verdict that MAY DIFFER from the committee's prior decision. "
        "Confirm the committee unless one side shows a clear, material flaw. "
        "Reply STRICTLY in the form:\n"
        "VERDICT=<BUY|HOLD|SELL>\nCONFIDENCE=<0-100>\nRATIONALE=<2-3 sentences>"))
    msg = HumanMessage(content=(
        f"Committee prior: {state['committee_decision']}\n\n"
        f"BULL case:\n{state['bull_case']}\n\n"
        f"BEAR case:\n{state['bear_case']}\n\n"
        f"Devil's critique:\n{state['devil_critique']}"))
    out = judge_model.invoke([sys_msg, msg])
    return {"judge_verdict": out.content, "final_decision": _parse_verdict(out.content)}

def build_debate():
    g = StateGraph(DebateState)
    g.add_node("bull", bull_node)
    g.add_node("bear", bear_node)
    g.add_node("devil", devil_advocate)
    g.add_node("judge", judge_node)
    g.add_edge(START, "bull")          # bull and bear in parallel…
    g.add_edge(START, "bear")
    g.add_edge("bull", "devil")        # …the devil waits for both
    g.add_edge("bear", "devil")
    g.add_edge("devil", "judge")
    g.add_edge("judge", END)
    return g.compile()


def run_pipeline(ticker: str) -> dict:
    committee_result = run_committee(ticker)                   # stage 1
    initial: DebateState = {
        "ticker": ticker.upper(),
        "committee_thesis": committee_result["pm_thesis"],
        "committee_decision": committee_result["final_decision"],
        "bull_case": "", "bear_case": "", "devil_critique": "",
        "judge_verdict": "", "final_decision": "",
    }
    debate_result = build_debate().invoke(initial)             # stage 2
    return {"committee": committee_result, "debate": debate_result}

def _conviction(text: str, side: str) -> str:
    m = re.search(rf"{side}_CONVICTION\s*=\s*(\d+)", text, re.I)
    return m.group(1) if m else "?"


if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "TSLA"
    out = run_pipeline(ticker)
    c, d = out["committee"], out["debate"]
    print("=" * 80)
    print(f"COMMITTEE said : {c['final_decision']}")
    print(f"DEBATE judge   : {d['final_decision']}   "
          f"(bull {_conviction(d['bull_case'], 'BULL')} vs bear {_conviction(d['bear_case'], 'BEAR')})")
    print("=" * 80)
    for title, key in (("Bull case", "bull_case"), ("Bear case", "bear_case"),
                       ("Devil's critique", "devil_critique"), ("Judge verdict", "judge_verdict")):
        print(f"\n--- {title} ---\n{d[key]}")
