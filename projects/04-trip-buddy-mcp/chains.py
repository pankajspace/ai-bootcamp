"""
chains.py
─────────
Multi-chain pipeline: DB → exact tool math → Chain 1 (cost breakdown) → Chain 2 (GO / NOT YET decision)
(based on trip_07_multi_chain.py).
"""

import math
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from db import fetch_place

load_dotenv()
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")


def get_base_llm() -> ChatOpenAI:
    """Return ChatOpenAI configured for reasoning or classic models."""
    if MODEL.startswith(("gpt-6", "gpt-5", "o1", "o3", "o4")):
        return ChatOpenAI(model=MODEL, reasoning_effort="none")
    return ChatOpenAI(model=MODEL, temperature=0)


@tool
def trip_cost_tool(
    travel_cost_per_person: float,
    room_price_per_night: float,
    daily_spend_per_person: float,
    people: int,
    nights: int,
) -> dict:
    """Compute rooms needed, stay share, food & fun, and total cost per person with exact arithmetic."""
    rooms_needed = math.ceil(people / 2)
    stay_share = round(rooms_needed * room_price_per_night * nights / people, 2)
    food_and_fun = round(daily_spend_per_person * nights, 2)
    total = round(travel_cost_per_person + stay_share + food_and_fun, 2)
    return {
        "rooms_needed": rooms_needed,
        "stay_share": stay_share,
        "food_and_fun": food_and_fun,
        "total_per_person": total,
    }


# ── Chain 1: explain the cost breakdown ──────────────────────────────────────
explain_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a trip planner for a group of friends.\n"
        "The numbers below were calculated by a trusted tool — do NOT redo them.\n"
        "Explain the cost breakdown in simple words and end with:\nCOST_PER_PERSON: {total_per_person}",
    ),
    (
        "human",
        "Trip: {name} ({trip_type}), best months {best_months}\n"
        "Group: {people} friends, {nights} nights at {stay_name}\n"
        "Travel: {travel_mode}, ₹{travel_cost_per_person} per person\n\n"
        "Tool results:\n"
        "  Rooms needed     : {rooms_needed}\n"
        "  Stay share       : ₹{stay_share}\n"
        "  Food and fun     : ₹{food_and_fun}\n"
        "  Total per person : ₹{total_per_person}",
    ),
])

# ── Chain 2: go / no-go decision (reads Chain 1's output) ────────────────────
decide_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are the group's money-minded friend.\n"
        "Money left per person = budget - total cost per person.\n"
        "Say clearly: GO (within budget) or NOT YET (over budget). "
        "If over budget, suggest one simple change (fewer nights, cheaper place, more friends).",
    ),
    (
        "human",
        "Trip: {name} | Budget per person: ₹{budget_per_person}\n\n"
        "Cost breakdown:\n{breakdown}",
    ),
])


def run_pipeline(place: str, people: int, nights: int, budget_per_person: float) -> dict:
    """DB → tool → chain 1 (breakdown) → chain 2 (GO / NOT YET decision)."""
    record = fetch_place(place)
    if not record:
        return {"error": f"Place '{place}' not found."}

    # Step 1: exact arithmetic via the tool (Python calls it directly, no LLM)
    tool_result = trip_cost_tool.invoke({
        "travel_cost_per_person": record["travel_cost_per_person"],
        "room_price_per_night":   record["room_price_per_night"],
        "daily_spend_per_person": record["daily_spend_per_person"],
        "people":                 people,
        "nights":                 nights,
    })

    llm = get_base_llm()
    explain_chain = explain_prompt | llm | StrOutputParser()
    decide_chain = decide_prompt | llm | StrOutputParser()

    # Step 2: Chain 1 explains the numbers
    breakdown = explain_chain.invoke({
        **record,
        **tool_result,
        "people": people,
        "nights": nights,
    })

    # Step 3: Chain 2 turns that explanation into a GO / NOT YET decision
    decision = decide_chain.invoke({
        "name":              record["name"],
        "budget_per_person": budget_per_person,
        "breakdown":         breakdown,
    })

    return {
        "place": record["name"],
        "people": people,
        "nights": nights,
        "budget_per_person": budget_per_person,
        "tool_result": tool_result,
        "breakdown": breakdown,
        "decision": decision,
    }


if __name__ == "__main__":
    plans = [
        ("Goa",    4, 3, 12000),
        ("Manali", 3, 4, 20000),
    ]
    for place, people, nights, budget in plans:
        print(f"\n{'=' * 60}")
        print(f"Plan: {place} — {people} friends, {nights} nights, ₹{budget} each")
        print("=" * 60)
        res = run_pipeline(place, people, nights, budget)
        print(f"\n[Tool] trip_cost_tool → {res['tool_result']}")
        print(f"\n--- Chain 1: Cost Breakdown ---\n{res['breakdown']}")
        print(f"\n--- Chain 2: Go or Not Yet ---\n{res['decision']}")

