"""
db.py
─────
3-table SQLite database (places, stays, costs) with 10 destinations from Bengaluru
(based on trip_07_multi_chain.py and trip_08_full_agent.py).
"""

import sqlite3

# check_same_thread=False so Gradio / async worker threads can share the connection
conn = sqlite3.connect(":memory:", check_same_thread=False)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.executescript("""
CREATE TABLE places (
    place_id TEXT PRIMARY KEY, name TEXT NOT NULL, trip_type TEXT,
    state TEXT, best_months TEXT
);
CREATE TABLE stays (
    place_id TEXT PRIMARY KEY, stay_name TEXT, room_price_per_night REAL NOT NULL,
    FOREIGN KEY (place_id) REFERENCES places(place_id)
);
CREATE TABLE costs (
    place_id TEXT PRIMARY KEY, travel_mode TEXT,
    travel_cost_per_person REAL NOT NULL, daily_spend_per_person REAL NOT NULL,
    FOREIGN KEY (place_id) REFERENCES places(place_id)
);
""")

# 4 kinds of trips: Beach, Hills, Heritage, Adventure. Prices are from Bengaluru.
cur.executemany("INSERT INTO places VALUES (?,?,?,?,?)", [
    ("GOA",       "Goa",         "Beach",     "Goa",              "Nov–Feb"),
    ("GOKARNA",   "Gokarna",     "Beach",     "Karnataka",        "Oct–Mar"),
    ("PONDY",     "Pondicherry", "Beach",     "Puducherry",       "Oct–Mar"),
    ("COORG",     "Coorg",       "Hills",     "Karnataka",        "Oct–Jun"),
    ("OOTY",      "Ooty",        "Hills",     "Tamil Nadu",       "Mar–Jun"),
    ("MANALI",    "Manali",      "Hills",     "Himachal Pradesh", "Mar–Jun"),
    ("HAMPI",     "Hampi",       "Heritage",  "Karnataka",        "Oct–Feb"),
    ("JAIPUR",    "Jaipur",      "Heritage",  "Rajasthan",        "Oct–Mar"),
    ("RISHIKESH", "Rishikesh",   "Adventure", "Uttarakhand",      "Oct–Jun"),
    ("DANDELI",   "Dandeli",     "Adventure", "Karnataka",        "Oct–May"),
])

cur.executemany("INSERT INTO stays VALUES (?,?,?)", [   # one room fits 2 people
    ("GOA",       "Sea Breeze Guesthouse",   3000), ("GOKARNA", "Om Beach Huts",          1800),
    ("PONDY",     "French Quarter Homestay", 2500), ("COORG",   "Coffee Estate Cottage",  2800),
    ("OOTY",      "Nilgiri View Lodge",      2200), ("MANALI",  "Old Manali Cafe Stay",   2500),
    ("HAMPI",     "Boulder View Guesthouse", 1500), ("JAIPUR",  "Pink City Haveli",       2400),
    ("RISHIKESH", "Ganga Riverside Camp",    1600), ("DANDELI", "Jungle River Camp",      2000),
])

cur.executemany("INSERT INTO costs VALUES (?,?,?,?)", [  # travel = return trip per person
    ("GOA",       "Overnight train", 2800, 1500), ("GOKARNA", "Overnight bus",   1200,  900),
    ("PONDY",     "Bus",             1400, 1200), ("COORG",   "Bus",             1000, 1100),
    ("OOTY",      "Bus",             1000, 1000), ("MANALI",  "Flight + bus",    9000, 1300),
    ("HAMPI",     "Overnight train",  900,  800), ("JAIPUR",  "Flight",          7500, 1200),
    ("RISHIKESH", "Flight + cab",    8500, 1400), ("DANDELI", "Bus",             1100, 1600),
])
conn.commit()


def fetch_place(place: str) -> dict | None:
    """JOIN places + stays + costs for one place (by id like 'PONDY' or name like 'Pondicherry')."""
    row = cur.execute("""
        SELECT p.place_id, p.name, p.trip_type, p.state, p.best_months,
               s.stay_name, s.room_price_per_night,
               c.travel_mode, c.travel_cost_per_person, c.daily_spend_per_person
        FROM places p
        JOIN stays s ON s.place_id = p.place_id
        JOIN costs c ON c.place_id = p.place_id
        WHERE UPPER(p.place_id) = UPPER(?) OR UPPER(p.name) = UPPER(?)
    """, (place.strip(), place.strip())).fetchone()
    return dict(row) if row else None


def list_places() -> list[dict]:
    """A short list of every destination."""
    return [dict(r) for r in cur.execute(
        "SELECT place_id, name, trip_type, best_months FROM places ORDER BY trip_type, name"
    ).fetchall()]

