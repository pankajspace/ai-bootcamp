"""
agent.py
────────
Trip Buddy Agent combining SQLite DB + ChromaDB RAG + Tool Calling
(based on trip_04_llm_chain.py, trip_05_rag_chain.py, and trip_06_tool_calling.py).
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from db import fetch_all_places
from rag import retrieve_context
from tools import TOOL_MAP, TOOLS

# Load .env from project folder or workspace root
load_dotenv()
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")


def _build_llm():
    """Create ChatOpenAI with reasoning_effort='none' for gpt-6-luna, or temperature=0 for classic models."""
    if MODEL.startswith(("gpt-6", "gpt-5", "o1", "o3", "o4")):
        base_llm = ChatOpenAI(model=MODEL, reasoning_effort="none")
    else:
        base_llm = ChatOpenAI(model=MODEL, temperature=0)
    return base_llm.bind_tools(TOOLS)


llm = _build_llm()

MAX_STEPS = 8

SYSTEM_TEMPLATE = """You are Trip Buddy, a friendly and accurate trip planner for a group of friends.

Rules:
1. Always fetch destination prices from the database using tools (`lookup_place`, `list_places`, or `find_trips_within_budget`). Never guess prices.
2. Always use the calculator tools (`calculate_stay_share`, `calculate_trip_cost`, or `find_trips_within_budget`) for arithmetic.
   - Rooms needed = people / 2, rounded UP (one room fits 2 people)
   - Stay share = rooms needed * room price per night * nights / people
   - Food and fun = daily spend per person * nights
   - Cost per person = travel cost + stay share + food and fun
3. When asked which trips fit a budget, present matching trips in a clean Markdown table with columns:
   `Destination | Estimated cost/person | Left from ₹<budget>`
   followed by a **Best value** summary, which destinations exceed the budget, and a helpful **Tip** grounded in the travel notebook.
4. Use the retrieved travel notebook tips below to give grounded seasonal, packing, room-splitting, and travel advice.

Relevant travel tips:
{rag_context}"""


def format_places_list() -> str:
    """Format all destinations from SQLite as a Markdown table when the user types 'list'."""
    rows = fetch_all_places()
    lines = [
        "Here are all the destinations in the database:\n",
        "| ID | Destination | Type | Stay | Room/night | Travel/person | Daily spend/person |",
        "| :--- | :--- | :--- | :--- | ---: | ---: | ---: |",
    ]
    for r in rows:
        lines.append(
            f"| `{r['place_id']}` | **{r['name']}** | {r['trip_type']} | {r['stay_name']} "
            f"| ₹{r['room_price_per_night']:,} | ₹{r['travel_cost_per_person']:,} | ₹{r['daily_spend_per_person']:,} |"
        )
    return "\n".join(lines)


def run_agent(user_question: str, history: list | None = None) -> str:
    """Run the RAG + tool-calling loop until the model gives a final answer."""
    if user_question.strip().lower() == "list":
        return format_places_list()

    # 1. RETRIEVE & AUGMENT: fetch relevant tips from ChromaDB
    rag_context = retrieve_context(user_question, n=4)
    system_prompt = SYSTEM_TEMPLATE.format(rag_context=rag_context)

    messages = [SystemMessage(content=system_prompt)]

    # Include prior chat history if provided by Gradio
    if history:
        for msg in history:
            if isinstance(msg, dict):
                role = msg.get("role")
                content = msg.get("content", "")
                if isinstance(content, list):
                    content = " ".join(
                        part.get("text", "") if isinstance(part, dict) else str(part)
                        for part in content
                    )
                if role == "user":
                    messages.append(HumanMessage(content=str(content)))
                elif role == "assistant":
                    messages.append(AIMessage(content=str(content)))
            elif isinstance(msg, (list, tuple)) and len(msg) == 2:
                user_msg, bot_msg = msg
                if user_msg:
                    messages.append(HumanMessage(content=str(user_msg)))
                if bot_msg:
                    messages.append(AIMessage(content=str(bot_msg)))

    messages.append(HumanMessage(content=user_question))

    # 2. TOOL-CALLING LOOP
    for _ in range(MAX_STEPS):
        response = llm.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            return response.text if hasattr(response, "text") else str(response.content)

        for tc in response.tool_calls:
            fn = TOOL_MAP[tc["name"]]
            result = fn.invoke(tc["args"])
            print(f"  [tool] {tc['name']}({tc['args']}) → {result}")
            messages.append(
                ToolMessage(
                    content=json.dumps(result),
                    tool_call_id=tc["id"],
                )
            )

    return "Stopped: too many tool calls without a final answer."

