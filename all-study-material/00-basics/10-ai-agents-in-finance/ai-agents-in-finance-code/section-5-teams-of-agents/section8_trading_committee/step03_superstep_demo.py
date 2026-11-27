"""
Section 8 — FREE demo (no API key, no LLM): how LangGraph runs a fan-out / fan-in graph
======================================================================================
Shows three things you will be asked about in interviews:
  1. SUPERSTEPS  – all nodes whose inputs are ready run together, then state is merged.
  2. IMPLICIT JOIN – a node with several incoming edges waits for ALL of them.
  3. REDUCERS    – two parallel nodes writing the SAME key crash… unless you add a reducer.

How to run:   python step03_superstep_demo.py
"""

import operator
import time
from typing import Annotated, TypedDict

from langgraph.errors import InvalidUpdateError
from langgraph.graph import END, START, StateGraph


def slow_node(name: str, key: str, seconds: float):
    """Build a node that 'thinks' for a while, then writes one key."""
    def node(state):
        time.sleep(seconds)                       # stands in for an LLM call
        return {key: f"{name} done"}
    return node


# --- 1 + 2: four analysts in parallel, each writing its OWN key -------------------
class Committee(TypedDict):
    fundamentals: str
    technicals: str
    sentiment: str
    macro: str
    pm: str


def pm_node(state: Committee):
    ready = [k for k in ("fundamentals", "technicals", "sentiment", "macro") if state[k]]
    return {"pm": f"PM saw {len(ready)}/4 reports"}


g = StateGraph(Committee)
for name in ("fundamentals", "technicals", "sentiment", "macro"):
    g.add_node(name, slow_node(name, name, 1.0))
    g.add_edge(START, name)                       # fan-out
    g.add_edge(name, "pm")                        # fan-in (implicit join)
g.add_node("pm", pm_node)
g.add_edge("pm", END)
committee = g.compile()

t0 = time.perf_counter()
empty = {"fundamentals": "", "technicals": "", "sentiment": "", "macro": "", "pm": ""}
for step, update in enumerate(committee.stream(empty, stream_mode="updates"), 1):
    print(f"t={time.perf_counter() - t0:4.1f}s  update {step}: {update}")
print("→ four 1-second analysts finished in about 1 second, then the PM ran once.\n")

# --- 3: two parallel nodes writing the SAME key ------------------------------------
class NoReducer(TypedDict):
    notes: str                                    # plain key: one writer per superstep


bad = StateGraph(NoReducer)
bad.add_node("bull", lambda s: {"notes": "bull says BUY"})
bad.add_node("bear", lambda s: {"notes": "bear says SELL"})
bad.add_edge(START, "bull")
bad.add_edge(START, "bear")
bad.add_edge("bull", END)
bad.add_edge("bear", END)
try:
    bad.compile().invoke({"notes": ""})
except InvalidUpdateError as e:
    print("Without a reducer →", type(e).__name__, ":", str(e).splitlines()[0])


class WithReducer(TypedDict):
    notes: Annotated[list[str], operator.add]     # reducer: concatenate the lists


good = StateGraph(WithReducer)
good.add_node("bull", lambda s: {"notes": ["bull says BUY"]})
good.add_node("bear", lambda s: {"notes": ["bear says SELL"]})
good.add_edge(START, "bull")
good.add_edge(START, "bear")
good.add_edge("bull", END)
good.add_edge("bear", END)
print("With operator.add  →", good.compile().invoke({"notes": []})["notes"])
