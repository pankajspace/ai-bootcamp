"""
rag.py
──────
13-tip travel notebook in ChromaDB with sentence-transformers embeddings
(based on trip_08_full_agent.py).
"""

import contextlib
import sys

# 13 travel notebook tips from trip_08_full_agent.py
KB = [
    ("trip-cost",    "Trip cost per person = travel + stay share + daily spend x nights.",                                  {"topic": "money"}),
    ("rooms",        "One room fits 2 people, so rooms needed = people / 2, rounded up. Stay share = rooms x room price x nights / people.", {"topic": "money"}),
    ("buffer",       "Keep a 10% buffer on top of the total for surprises like a cab surge or a missed bus.",                {"topic": "money"}),
    ("splitting",    "Split shared costs (stay, cabs, fuel) equally. Personal shopping is never split.",                     {"topic": "money"}),
    ("beach",        "Beach trips (Goa, Gokarna, Pondicherry): best November-February. In the monsoon (June-September) many beach shacks and water sports close.", {"topic": "trip_type"}),
    ("hills",        "Hill trips (Coorg, Ooty, Manali): best March-June and October. Avoid July-August: heavy rain and landslides block hill roads. Carry a jacket even in summer.", {"topic": "trip_type"}),
    ("heritage",     "Heritage trips (Hampi, Jaipur): best October-March. April-May afternoons cross 40°C, so explore early in the morning.", {"topic": "trip_type"}),
    ("adventure",    "Adventure trips (Rishikesh, Dandeli): river rafting runs October-June and closes in the monsoon. Use licensed operators and always wear a life jacket.", {"topic": "trip_type"}),
    ("book-early",   "Book trains and flights 30-60 days early; prices often double in the last week.",                     {"topic": "travel_tip"}),
    ("weekdays",     "Weekday stays are often 20-30% cheaper than weekends.",                                                {"topic": "travel_tip"}),
    ("long-weekend", "Long weekends and New Year push Goa prices up sharply; book early or pick Gokarna instead.",           {"topic": "travel_tip"}),
    ("overnight",    "Overnight buses and trains save the cost of one night's stay.",                                       {"topic": "travel_tip"}),
    ("big-group",    "Groups bigger than 6: a villa or homestay is usually cheaper than many hotel rooms.",                 {"topic": "travel_tip"}),
]

_embed = None
_col = None


def _init_vector_store():
    """Initialize HuggingFaceEmbeddings and ChromaDB (redirecting stdout to stderr for MCP stdio safety)."""
    global _embed, _col
    if _col is not None:
        return True
    try:
        with contextlib.redirect_stdout(sys.stderr):
            import chromadb
            from langchain_huggingface import HuggingFaceEmbeddings

            _embed = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
            chroma = chromadb.Client()
            _col = chroma.get_or_create_collection("trip_tips", metadata={"hnsw:space": "cosine"})
            if _col.count() == 0:
                vecs = _embed.embed_documents([t for _, t, _ in KB])
                _col.add(
                    ids=[i for i, _, _ in KB],
                    embeddings=vecs,
                    documents=[t for _, t, _ in KB],
                    metadatas=[m for _, _, m in KB],
                )
        return True
    except Exception as exc:
        print(f"[rag] ChromaDB/HuggingFaceEmbeddings unavailable ({exc}), using keyword fallback.", file=sys.stderr)
        return False


def retrieve_context(query: str, n: int = 3) -> str:
    """Top-n notebook tips for this question, as bullet points."""
    if _init_vector_store() and _col is not None and _embed is not None:
        qv = _embed.embed_query(query)
        res = _col.query(query_embeddings=[qv], n_results=n)
        return "\n".join(f"- {c}" for c in res["documents"][0])

    # Fallback scoring by word overlap if vector store packages are not installed yet
    q_words = set(query.lower().split())
    scored = sorted(
        KB,
        key=lambda item: sum(1 for w in q_words if w in item[1].lower()),
        reverse=True,
    )
    return "\n".join(f"- {t}" for _, t, _ in scored[:n])


def get_tip_count() -> int:
    """Return number of tips in the knowledge base."""
    if _col is not None:
        return _col.count()
    return len(KB)

