import json
import os
from pathlib import Path
from dotenv import load_dotenv

import boto3
import chromadb
import numpy as np
from strands import Agent
from strands.models.bedrock import BedrockModel

# Load environment variables from the .env file
load_dotenv()

MODEL_ID = os.getenv("AWS_BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
EMBED_MODEL_ID = os.getenv("AWS_BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")

# Initialize the AWS Bedrock Runtime client (used to invoke Titan Embeddings)
bedrock = boto3.client("bedrock-runtime")


# ==============================================================================
# HELPER: Convert text into a vector using AWS Titan Text Embeddings V2
# ==============================================================================
# What is an Embedding?
#   - An embedding turns text into an array of floating-point numbers (e.g. 512 numbers)
#     where texts with similar meanings point in the same direction in vector space.
#   - Titan V2 (`amazon.titan-embed-text-v2:0`) returns normalized vectors (`normalize=True`),
#     meaning the dot product (`np.dot(vec_a, vec_b)`) equals Cosine Similarity (-1 to 1).
# ==============================================================================
def get_titan_embedding(text: str) -> list[float]:
    response = bedrock.invoke_model(
        modelId=EMBED_MODEL_ID,
        body=json.dumps({"inputText": text, "dimensions": 512, "normalize": True}),
    )
    # Read the streaming body bytes from Bedrock, parse the JSON, and return the 512-float list
    return json.loads(response["body"].read())["embedding"]


# ==============================================================================
# STEP 1: VECTOR CHUNKING (Splitting Document with Overlap)
# ==============================================================================
# Why chunk with overlap?
#   - Embedding models work best on focused passages rather than entire books.
#   - Using an `overlap` (e.g. 400 chars with 50-char overlap -> step of 350 chars)
#     ensures that sentences split at the boundary of one chunk remain intact in the next.
# ==============================================================================
# Resolve `sample_rag_knowledge.txt` in the same folder as this script and read its full text
text = (Path(__file__).parent / "sample_rag_knowledge.txt").read_text(encoding="utf-8")

chunk_size, overlap = 400, 50
# Slide a 400-character window across `text`, advancing by 350 chars (`chunk_size - overlap`)
# at each step so every chunk shares 50 characters of context with the previous chunk
chunks = [text[i : i + chunk_size].strip() for i in range(0, len(text), chunk_size - overlap)]

print("=== 1. Chunking ===")
print(f"Split knowledge base ({len(text)} chars) into {len(chunks)} overlapping chunks.\n")


# ==============================================================================
# STEP 2: EMBEDDING & STORING IN CHROMADB
# ==============================================================================
# We embed each chunk with AWS Titan Embeddings and store both the text (`documents`)
# and the vectors (`embeddings`) inside an in-memory ChromaDB collection.
# ==============================================================================
print(f"=== 2. Embedding & Storing in ChromaDB ({EMBED_MODEL_ID}) ===")
chroma_client = chromadb.EphemeralClient()
collection = chroma_client.create_collection(
    name="knowledge_base",
    metadata={"hnsw:space": "cosine"},  # Use cosine distance for vector similarity search
)

collection.add(
    # Generate a unique ID for each chunk: ["chunk_0", "chunk_1", ...]
    ids=[f"chunk_{i}" for i in range(len(chunks))],
    documents=chunks,
    # Convert every text chunk into a 512-dimensional Titan vector
    embeddings=[get_titan_embedding(c) for c in chunks],
)
print(f"Indexed {collection.count()} chunks into ChromaDB.\n")


# ==============================================================================
# STEP 3: RETRIEVAL OF TOP 5 ANSWERS
# ==============================================================================
# We embed the user's question with Titan Embeddings and query ChromaDB for the
# Top 5 closest chunks using cosine distance (Cosine Similarity = 1 - Distance).
# ==============================================================================
query = "What happens to customer data when an account is canceled, and when can I get a refund?"
print("=== 3. Retrieving Top 5 Answers from ChromaDB ===")
print(f"Query: {query}\n")

query_vec = get_titan_embedding(query)
results = collection.query(query_embeddings=[query_vec], n_results=5)
# ChromaDB supports batch queries, so `documents` and `distances` are lists of lists;
# `[0]` extracts the Top 5 results for our single query
top_5_docs = results["documents"][0]
top_5_dists = results["distances"][0]

# Pair each retrieved document with its cosine distance and number them starting from Rank #1
for rank, (doc, dist) in enumerate(zip(top_5_docs, top_5_dists), 1):
    # `1 - dist` converts cosine distance into cosine similarity; `replace(chr(10), ' ')` flattens newlines for preview
    print(f"  Rank #{rank} (Score: {1 - dist:.4f}): {doc[:75].replace(chr(10), ' ')}...")


# ==============================================================================
# STEP 4: RERANKING TOP 5 USING AWS TITAN EMBEDDINGS
# ==============================================================================
# Why rerank?
#   - Initial retrieval embeds a whole 400-char chunk at once, which can dilute
#     the score if only one sentence inside the chunk answers the question.
#   - Reranking inspects ONLY the Top 5 chunks closely: we embed individual lines
#     with Titan Embeddings and rank each chunk by its best-matching sentence (`np.dot`).
# ==============================================================================
print("\n=== 4. Reranking Top 5 with AWS Titan Embeddings ===")

def score_chunk(chunk_text: str) -> float:
    # Split chunk into non-trivial lines (> 20 chars); fall back to the full chunk if no lines match
    lines = [line.strip() for line in chunk_text.split("\n") if len(line.strip()) > 20] or [chunk_text]
    # Embed each line with Titan, compute cosine similarity (`np.dot`) against `query_vec`, and keep the highest score
    return max(float(np.dot(query_vec, get_titan_embedding(line))) for line in lines)

# Compute `(rerank_score, chunk_text)` for each of the Top 5 chunks and sort highest score first (`reverse=True`)
reranked = sorted(
    [(score_chunk(doc), doc) for doc in top_5_docs],
    key=lambda x: x[0],
    reverse=True,
)

for rank, (score, doc) in enumerate(reranked, 1):
    print(f"  New Rank #{rank} (Rerank Score: {score:.4f}): {doc[:75].replace(chr(10), ' ')}...")


# ==============================================================================
# STEP 5: GENERATE GROUNDED ANSWER WITH STRANDS AGENT
# ==============================================================================
# Pass the top reranked chunks as context to the Bedrock Strands Agent.
# ==============================================================================
print(f"\n=== 5. Grounded Answer from Agent ({MODEL_ID}) ===")
# Unpack the Top 3 `(score, doc)` tuples from `reranked` and join their text with blank lines
context = "\n\n".join(doc for _, doc in reranked[:3])

agent = Agent(
    model=BedrockModel(model_id=MODEL_ID),
    system_prompt="Answer the user's question using ONLY the provided context.",
    callback_handler=None,
)

print(agent(f"Context:\n{context}\n\nQuestion: {query}"))
