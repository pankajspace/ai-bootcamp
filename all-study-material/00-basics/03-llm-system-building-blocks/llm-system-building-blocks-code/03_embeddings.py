"""Worked example: getting a real embedding (a list of numbers that captures meaning)."""
from _common import EMBEDDING_MODEL, get_client

client = get_client()

emb = client.embeddings.create(
    model=EMBEDDING_MODEL,
    input="How do I reset my UPI PIN?",
)
vector = emb.data[0].embedding
print(len(vector))      # how many numbers?  (1536 for text-embedding-3-small)
print(vector[:5])       # first five numbers
