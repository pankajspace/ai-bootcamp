"""
tools.py
────────
LangChain tools for looking up destinations in SQLite and doing exact trip cost maths
(based on trip_06_tool_calling.py).
"""

import math
from langchain_core.tools import tool
from db import fetch_all_places, fetch_place


@tool
def calculate_stay_share(room_price_per_night: float, nights: int, people: int) -> dict:
    """
    Calculate how much each person pays for the stay.
    One room fits 2 people, so rooms_needed = people / 2 rounded up.
    stay_share = rooms_needed * room_price_per_night * nights / people
    """
    rooms_needed = math.ceil(people / 2)
    stay_share = round(rooms_needed * room_price_per_night * nights / people, 2)
    return {"rooms_needed": rooms_needed, "stay_share": stay_share}


@tool
def calculate_trip_cost(
    travel_cost_per_person: float,
    stay_share: float,
    daily_spend_per_person: float,
    nights: int,
) -> float:
    """
    Calculate the total trip cost for one person.
    total = travel_cost_per_person + stay_share + daily_spend_per_person * nights
    """
    return round(travel_cost_per_person + stay_share + daily_spend_per_person * nights, 2)


@tool
def lookup_place(place: str) -> dict:
    """
    Look up a destination's stay and prices from the SQLite database.
    Returns: place, trip_type, stay_name, room_price_per_night, travel_cost_per_person, daily_spend_per_person
    """
    record = fetch_place(place)
    if not record:
        return {"error": f"{place} not found"}
    return {
        "place": record["name"],
        "trip_type": record["trip_type"],
        "stay_name": record["stay_name"],
        "room_price_per_night": record["room_price_per_night"],
        "travel_cost_per_person": record["travel_cost_per_person"],
        "daily_spend_per_person": record["daily_spend_per_person"],
    }


@tool
def list_places() -> list[dict]:
    """
    List all destinations in the SQLite database with their trip_type, stay_name, and prices.
    """
    return fetch_all_places()


@tool
def find_trips_within_budget(budget_per_person: float, people: int, nights: int) -> dict:
    """
    Compare all destinations in the database for a group of `people` and `nights` against `budget_per_person`.
    Computes exact rooms_needed, stay_share, estimated_cost_per_person, and left_from_budget.
    """
    rooms_needed = math.ceil(people / 2)
    within_budget = []
    exceeds_budget = []

    for row in fetch_all_places():
        stay_share = round(rooms_needed * row["room_price_per_night"] * nights / people, 2)
        total = round(
            row["travel_cost_per_person"] + stay_share + row["daily_spend_per_person"] * nights,
            2,
        )
        left = round(budget_per_person - total, 2)
        entry = {
            "place": row["name"],
            "trip_type": row["trip_type"],
            "stay_name": row["stay_name"],
            "rooms_needed": rooms_needed,
            "stay_share": stay_share,
            "estimated_cost_per_person": round(total),
            "exact_cost_per_person": total,
            "left_from_budget": round(left),
        }
        if total <= budget_per_person:
            within_budget.append(entry)
        else:
            exceeds_budget.append(entry)

    within_budget.sort(key=lambda x: x["exact_cost_per_person"])
    exceeds_budget.sort(key=lambda x: x["exact_cost_per_person"])

    return {
        "people": people,
        "nights": nights,
        "rooms_needed": rooms_needed,
        "budget_per_person": budget_per_person,
        "within_budget": within_budget,
        "exceeds_budget": [x["place"] for x in exceeds_budget],
    }


TOOLS = [
    lookup_place,
    list_places,
    calculate_stay_share,
    calculate_trip_cost,
    find_trips_within_budget,
]

TOOL_MAP = {t.name: t for t in TOOLS}

