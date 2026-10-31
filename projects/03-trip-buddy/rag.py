"""
rag.py
──────
ChromaDB + HuggingFaceEmbeddings travel notebook retrieval
(based on trip_02_embeddings_basics.py, trip_03_chromadb_retrieval.py, and trip_05_rag_chain.py).
"""

import chromadb
from langchain_huggingface import HuggingFaceEmbeddings

# Travel notebook tips with topic metadata ("money", "trip_type", "travel_tip")
DOCS = [
    {
        "id": "trip-cost",
        "text": "Trip cost per person = travel + stay share + daily spend x nights.",
        "meta": {"topic": "money"},
    },
    {
        "id": "rooms",
        "text": "One room fits 2 people, so rooms needed = people / 2, rounded up. Stay share = rooms x room price x nights / people.",
        "meta": {"topic": "money"},
    },
    {
        "id": "buffer",
        "text": "Keep a 10% buffer on top of the total for surprises like a cab surge or a missed bus.",
        "meta": {"topic": "money"},
    },
    {
        "id": "beach",
        "text": "Beach trips (Goa, Gokarna, Pondicherry): best November-February. In the monsoon many beach shacks and water sports close.",
        "meta": {"topic": "trip_type"},
    },
    {
        "id": "hills",
        "text": "Hill trips (Coorg, Ooty, Manali): best March-June and October. Avoid July-August: heavy rain and landslides block hill roads. Carry a jacket.",
        "meta": {"topic": "trip_type"},
    },
    {
        "id": "heritage",
        "text": "Heritage trips (Hampi, Jaipur): old temples, forts and palaces. Best October-March; explore early in the morning as April-May afternoons cross 40°C.",
        "meta": {"topic": "trip_type"},
    },
    {
        "id": "adventure",
        "text": "Adventure trips (Rishikesh, Dandeli): river rafting runs October-June and closes in the monsoon.",
        "meta": {"topic": "trip_type"},
    },
    {
        "id": "book-early",
        "text": "Book trains and flights 30-60 days early; prices often double in the last week.",
        "meta": {"topic": "travel_tip"},
    },
    {
        "id": "weekdays",
        "text": "Weekday stays are often 20-30% cheaper than weekends.",
        "meta": {"topic": "travel_tip"},
    },
    {
        "id": "pack",
        "text": "Mountain weather changes fast: carry a rain jacket and warm layers even in summer.",
        "meta": {"topic": "travel_tip"},
    },
    {
        "id": "overnight",
        "text": "Gokarna and Hampi have overnight travel options, which can help save a night's stay if your itinerary lines up.",
        "meta": {"topic": "travel_tip"},
    },
]

# Build embeddings and ChromaDB collection once at startup
embed = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

client = chromadb.Client()
collection = client.get_or_create_collection(
    "trip_tips",
    metadata={"hnsw:space": "cosine"},
)

if collection.count() == 0:
    vectors = embed.embed_documents([d["text"] for d in DOCS])
    collection.add(
        ids=[d["id"] for d in DOCS],
        embeddings=vectors,
        documents=[d["text"] for d in DOCS],
        metadatas=[d["meta"] for d in DOCS],
    )


def retrieve(query: str, n: int = 3, where: dict | None = None) -> list[str]:
    """Find the n tips closest in meaning to `query`, optionally filtered by metadata."""
    qv = embed.embed_query(query)
    kwargs = {"query_embeddings": [qv], "n_results": n}
    if where:
        kwargs["where"] = where
    results = collection.query(**kwargs)
    return results["documents"][0]


def retrieve_context(query: str, n: int = 4) -> str:
    """RETRIEVE step: find the n most relevant tips and return them as a bullet list."""
    tips = retrieve(query, n=n)
    return "\n".join(f"- {tip}" for tip in tips)

