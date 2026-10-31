"""
db.py
─────
SQLite database for Trip Buddy destinations and stays (based on trip_01_sqlite_basics.py).
"""

import sqlite3

# Keep a shared in-memory SQLite connection (check_same_thread=False for Gradio worker threads)
conn = sqlite3.connect(":memory:", check_same_thread=False)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# ── 1. Create the tables ──────────────────────────────────────────────────────
cur.executescript("""
CREATE TABLE places (
    place_id               TEXT PRIMARY KEY,
    name                   TEXT NOT NULL,
    trip_type              TEXT NOT NULL,
    travel_cost_per_person INTEGER NOT NULL,
    daily_spend_per_person INTEGER NOT NULL
);

CREATE TABLE stays (
    place_id             TEXT PRIMARY KEY,
    stay_name            TEXT NOT NULL,
    room_price_per_night INTEGER NOT NULL,
    FOREIGN KEY (place_id) REFERENCES places(place_id)
);
""")

# ── 2. Seed destinations and stays ────────────────────────────────────────────
cur.executemany("INSERT INTO places VALUES (?, ?, ?, ?, ?)", [
    ("GOA",         "Goa",         "Beach",     2800, 1500),
    ("COORG",       "Coorg",       "Hills",     1000, 1100),
    ("HAMPI",       "Hampi",       "Heritage",   900,  800),
    ("MANALI",      "Manali",      "Hills",     9000, 1300),
    ("GOKARNA",     "Gokarna",     "Beach",     1200,  900),
    ("OOTY",        "Ooty",        "Hills",     1000, 1000),
    ("DANDELI",     "Dandeli",     "Adventure", 1500, 1400),
    ("PONDICHERRY", "Pondicherry", "Beach",     1400, 1200),
    ("RISHIKESH",   "Rishikesh",   "Adventure", 6500, 1200),
    ("JAIPUR",      "Jaipur",      "Heritage",  7000, 1300),
])

cur.executemany("INSERT INTO stays VALUES (?, ?, ?)", [
    ("GOA",         "Sea Breeze Guesthouse",  3000),
    ("COORG",       "Coffee Estate Cottage",  2800),
    ("HAMPI",       "Boulder View Guesthouse", 1500),
    ("MANALI",      "Snow Peak Chalet",       2500),
    ("GOKARNA",     "Sunset Shack Homestay",  1800),
    ("OOTY",        "Misty Hills Bungalow",   2200),
    ("DANDELI",     "River Edge Jungle Camp", 2000),
    ("PONDICHERRY", "French Quarter Villa",   2500),
    ("RISHIKESH",   "Ganga Rapids Camp",      2200),
    ("JAIPUR",      "Pink City Haveli",       2600),
])

conn.commit()


# ── 3. Lookup helpers ─────────────────────────────────────────────────────────
def fetch_place(place: str) -> dict | None:
    """Return one place (with its stay and prices) as a dict, or None if not found."""
    row = cur.execute(
        "SELECT p.place_id, p.name, p.trip_type, "
        "       s.stay_name, s.room_price_per_night, "
        "       p.travel_cost_per_person, p.daily_spend_per_person "
        "FROM places p "
        "JOIN stays s ON s.place_id = p.place_id "
        "WHERE UPPER(p.place_id) = UPPER(?) OR UPPER(p.name) = UPPER(?)",
        (place.strip(), place.strip()),
    ).fetchone()
    return dict(row) if row else None


def fetch_all_places() -> list[dict]:
    """Return all destinations with their stay and cost details."""
    rows = cur.execute(
        "SELECT p.place_id, p.name, p.trip_type, "
        "       s.stay_name, s.room_price_per_night, "
        "       p.travel_cost_per_person, p.daily_spend_per_person "
        "FROM places p "
        "JOIN stays s ON s.place_id = p.place_id "
        "ORDER BY p.name"
    ).fetchall()
    return [dict(r) for r in rows]

