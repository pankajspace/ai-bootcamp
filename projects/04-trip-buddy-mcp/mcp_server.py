"""
mcp_server.py
─────────────
MCP Tool Server over stdio exposing Trip Buddy's 3-table SQLite DB, ChromaDB RAG notebook,
exact cost calculator, and multi-chain pipeline.

Run directly:
    python mcp_server.py
"""

import math
import sys
from typing import Any

# Support both mcp 2.x (MCPServer) and mcp 1.x (FastMCP)
try:
    from mcp.server.mcpserver import MCPServer as FastMCP
except ImportError:
    from mcp.server.fastmcp import FastMCP

from chains import run_pipeline
from db import fetch_place, list_places
from rag import retrieve_context

mcp = FastMCP("Trip-Buddy-MCP-Server")


@mcp.tool(
    description=(
        "Fetch a destination's trip type, state, best months, stay, room price, "
        "travel mode, travel cost, and daily spend from the database."
    )
)
def db_lookup(place: str) -> dict[str, Any]:
    print(f"[mcp-server] db_lookup({place!r})", file=sys.stderr)
    record = fetch_place(place)
    return record if record else {"error": f"{place} not found. Use list_destinations to see valid places."}


@mcp.tool(description="Return all destinations in the database.")
def list_destinations() -> list[dict[str, Any]]:
    print("[mcp-server] list_destinations()", file=sys.stderr)
    return list_places()


@mcp.tool(
    description=(
        "Compute the trip cost per person with exact arithmetic. "
        "One room fits 2 people. Returns: rooms_needed, stay_share_per_person, "
        "food_and_fun_per_person, total_per_person, and (if budget_per_person is given) "
        "within_budget and money_left_per_person (negative = over budget)."
    )
)
def compute_trip_cost(
    travel_cost_per_person: float,
    room_price_per_night: float,
    daily_spend_per_person: float,
    people: int,
    nights: int,
    budget_per_person: float | None = None,
) -> dict[str, Any]:
    print(
        f"[mcp-server] compute_trip_cost(people={people}, nights={nights}, budget={budget_per_person})",
        file=sys.stderr,
    )
    rooms_needed = math.ceil(people / 2)
    stay_share = round(rooms_needed * room_price_per_night * nights / people, 2)
    food_and_fun = round(daily_spend_per_person * nights, 2)
    total = round(travel_cost_per_person + stay_share + food_and_fun, 2)
    result: dict[str, Any] = {
        "rooms_needed": rooms_needed,
        "stay_share_per_person": stay_share,
        "food_and_fun_per_person": food_and_fun,
        "total_per_person": total,
    }
    if budget_per_person is not None:
        result["within_budget"] = total <= budget_per_person
        result["money_left_per_person"] = round(budget_per_person - total, 2)
    return result


@mcp.tool(description="Retrieve top-n relevant travel tips from the ChromaDB travel notebook.")
def retrieve_travel_tips(query: str, n: int = 3) -> str:
    print(f"[mcp-server] retrieve_travel_tips({query!r}, n={n})", file=sys.stderr)
    return retrieve_context(query, n=n)


@mcp.tool(
    description=(
        "Run the 2-step multi-chain pipeline (DB -> exact tool cost -> Chain 1 breakdown "
        "-> Chain 2 GO / NOT YET decision) for a specific destination, group size, nights, and budget."
    )
)
def evaluate_trip_plan(
    place: str,
    people: int,
    nights: int,
    budget_per_person: float,
) -> dict[str, Any]:
    print(
        f"[mcp-server] evaluate_trip_plan(place={place!r}, people={people}, nights={nights}, budget={budget_per_person})",
        file=sys.stderr,
    )
    return run_pipeline(place, people, nights, budget_per_person)


if __name__ == "__main__":
    mcp.run(transport="stdio")

