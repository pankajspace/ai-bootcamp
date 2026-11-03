"""
Demo 8: Retrieval-Augmented Generation (RAG) with AWS Titan Embeddings & ChromaDB
=================================================================================

This script explains and demonstrates the complete 5-stage RAG pipeline:
1. Document Chunking: Splitting a source text file into overlapping chunks so
   semantic context isn't lost across boundaries.
2. Vector Embedding: Converting text chunks into dense numerical vectors using
   Amazon Titan Text Embeddings V2 (`amazon.titan-embed-text-v2:0`) on AWS Bedrock.
3. Vector Storage (ChromaDB): Indexing the chunks and their Titan embeddings
   inside a ChromaDB vector collection.
4. Top-5 Retrieval: Encoding a user query with Titan Embeddings and retrieving
   the top 5 candidate chunks from ChromaDB using vector similarity search.
5. Reranking & Grounded Generation: Re-scoring the top 5 candidates using
   fine-grained Titan sentence-level embeddings + keyword overlap (hybrid reranking)
   to surface the most relevant context, and passing it to a Strands Agent on
   AWS Bedrock to generate an accurate, grounded answer.
"""

import json
import math
import os
import re
from pathlib import Path
from dotenv import load_dotenv

import boto3
import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from strands import Agent
from strands.models.bedrock import BedrockModel

# Load environment variables from the .env file
load_dotenv()

# Bedrock LLM for final answer generation and Titan Embedding model ID
MODEL_ID = os.getenv("AWS_BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
TITAN_EMBED_MODEL_ID = os.getenv(
    "AWS_BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0"
)
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

# Path to our sample knowledge base text file
SAMPLE_TEXT_PATH = Path(__file__).parent / "sample_rag_knowledge.txt"


# ==============================================================================
# STEP 1: VECTOR CHUNKING (Sliding Window with Overlap)
# ==============================================================================
# Why chunking?
#   - Embedding models have token limits and perform best on focused passages
#     rather than entire multi-page documents.
#   - Adding `chunk_overlap` ensures sentences or ideas split at the edge of one
#     chunk are preserved intact in the next chunk.
# ==============================================================================
def chunk_text(
    text: str, chunk_size: int = 450, chunk_overlap: int = 75
) -> list[dict]:
    """
    Split a document into overlapping character chunks while respecting
    paragraph and sentence boundaries where possible.
    """
    # Normalize excessive blank lines
    cleaned = re.sub(r"\n{3,}", "\n\n", text.strip())

    chunks: list[dict] = []
    start = 0
    text_length = len(cleaned)
    chunk_index = 0

    while start < text_length:
        end = min(start + chunk_size, text_length)

        # If we are not at the end of the text, try to break cleanly at a newline or period
        if end < text_length:
            newline_pos = cleaned.rfind("\n", start + chunk_overlap, end)
            period_pos = cleaned.rfind(". ", start + chunk_overlap, end)
            break_pos = max(newline_pos, period_pos)
            if break_pos != -1 and break_pos > start:
                end = break_pos + 1

        chunk_content = cleaned[start:end].strip()
        if chunk_content:
            chunks.append(
                {
                    "id": f"chunk_{chunk_index:02d}",
                    "text": chunk_content,
                    "start_char": start,
                    "end_char": end,
                }
            )
            chunk_index += 1

        if end >= text_length:
            break

        # Advance window forward, stepping back by `chunk_overlap` characters
        start = max(end - chunk_overlap, start + 1)

    return chunks


# ==============================================================================
# STEP 2: EMBEDDING WITH AWS TITAN EMBEDDINGS V2
# ==============================================================================
# Why embeddings?
#   - Embeddings convert text into a fixed-length vector of floating-point numbers
#     (e.g., 512 or 1024 dimensions) where semantically similar texts point in
#     similar directions in vector space.
#   - Amazon Titan Text Embeddings V2 (`amazon.titan-embed-text-v2:0`) supports
#     256, 512, or 1024 dimensions and returns normalized vectors out of the box.
# ==============================================================================
class TitanEmbeddingFunction(EmbeddingFunction[Documents]):
    """
    Custom ChromaDB-compatible EmbeddingFunction backed by AWS Bedrock Titan Embeddings.
    """

    def __init__(
        self,
        model_id: str = TITAN_EMBED_MODEL_ID,
        region_name: str = AWS_REGION,
        dimensions: int = 512,
    ):
        self.model_id = model_id
        self.dimensions = dimensions
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime", region_name=region_name
        )

    def embed_single(self, text: str) -> list[float]:
        """Call AWS Bedrock Titan Text Embeddings V2 for a single text string."""
        payload = {
            "inputText": text,
            "dimensions": self.dimensions,
            "normalize": True,
        }
        response = self.bedrock_runtime.invoke_model(
            modelId=self.model_id,
            body=json.dumps(payload),
            accept="application/json",
            contentType="application/json",
        )
        response_body = json.loads(response["body"].read())
        return response_body["embedding"]

    def __call__(self, input: Documents) -> Embeddings:
        """Batch-embed a list of documents for ChromaDB."""
        return [self.embed_single(doc) for doc in input]


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors:
        cos(theta) = (A . B) / (||A|| * ||B||)
    Ranges from -1.0 (opposite) to 1.0 (identical meaning).
    """
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)


# ==============================================================================
# STEP 3: STORING VECTORS IN CHROMADB
# ==============================================================================
def build_chroma_vector_store(
    chunks: list[dict], titan_ef: TitanEmbeddingFunction
) -> chromadb.Collection:
    """
    Store document chunks and their AWS Titan embeddings in ChromaDB.
    Uses EphemeralClient (in-memory) so the demo runs cleanly without setup.
    """
    chroma_client = chromadb.EphemeralClient()

    # Create a collection configured with cosine distance and our Titan embedder
    collection = chroma_client.get_or_create_collection(
        name="acme_cloud_handbook",
        embedding_function=titan_ef,
        metadata={"hnsw:space": "cosine"},
    )

    collection.upsert(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[
            {
                "chunk_id": c["id"],
                "start_char": c["start_char"],
                "end_char": c["end_char"],
                "source": SAMPLE_TEXT_PATH.name,
            }
            for c in chunks
        ],
    )
    return collection


# ==============================================================================
# STEP 4: RETRIEVAL OF TOP 5 CANDIDATE ANSWERS
# ==============================================================================
def retrieve_top_k(
    collection: chromadb.Collection, query: str, top_k: int = 5
) -> list[dict]:
    """
    Embed the user query with Titan Embeddings and retrieve the Top 5 closest
    chunks from ChromaDB based on cosine distance.
    """
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    candidates = []
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    for rank, (doc, meta, dist) in enumerate(
        zip(docs, metas, distances), start=1
    ):
        # For cosine distance in ChromaDB: cosine_similarity = 1.0 - cosine_distance
        bi_encoder_sim = round(1.0 - float(dist), 4)
        candidates.append(
            {
                "initial_rank": rank,
                "chunk_id": meta["chunk_id"],
                "text": doc,
                "bi_encoder_score": bi_encoder_sim,
            }
        )
    return candidates


# ==============================================================================
# STEP 5: RERANKING USING AWS TITAN EMBEDDINGS (Sentence-Level MaxSim + Lexical)
# ==============================================================================
# Why rerank?
#   - Initial retrieval (Stage 1) compares the query vector against an entire
#     450-character chunk vector. Long chunks that discuss multiple topics can
#     dilute the overall chunk embedding.
#   - Reranking (Stage 2) inspects ONLY the Top 5 retrieved candidates in detail:
#     1. Titan Fine-Grained MaxSim: Embeds the individual sentences inside each
#        candidate chunk using AWS Titan Embeddings and computes the maximum
#        sentence-to-query cosine similarity (ColBERT / MaxSim style).
#     2. Lexical / Keyword Overlap: Boosts chunks that contain exact technical
#        terms, error codes, or numbers from the query.
#     3. Combined Rerank Score: Re-orders the Top 5 candidates so the best
#        passages sit at Rank #1.
# ==============================================================================
def rerank_with_titan(
    query: str,
    candidates: list[dict],
    titan_ef: TitanEmbeddingFunction,
) -> list[dict]:
    """
    Rerank the Top 5 retrieved chunks using AWS Titan Embeddings sentence-level
    MaxSim combined with chunk similarity and keyword overlap.
    """
    query_vec = titan_ef.embed_single(query)
    query_terms = {
        tok
        for tok in re.findall(r"[a-z0-9]+", query.lower())
        if len(tok) > 2
    }

    reranked = []
    for item in candidates:
        chunk_text_str = item["text"]

        # Split candidate chunk into individual sentences/lines for fine-grained Titan scoring
        sentences = [
            s.strip()
            for s in re.split(r"(?<=[.!?])\s+|\n+", chunk_text_str)
            if len(s.strip()) > 15
        ]
        if not sentences:
            sentences = [chunk_text_str]

        # Compute Titan embedding similarity for each sentence and take MaxSim
        sentence_scores = [
            cosine_similarity(query_vec, titan_ef.embed_single(sentence))
            for sentence in sentences
        ]
        max_sentence_sim = max(sentence_scores)

        # Compute exact keyword overlap ratio
        chunk_terms = set(re.findall(r"[a-z0-9]+", chunk_text_str.lower()))
        keyword_overlap = (
            len(query_terms & chunk_terms) / len(query_terms)
            if query_terms
            else 0.0
        )

        # Weighted hybrid rerank score:
        # 50% Titan sentence-level MaxSim + 35% Titan whole-chunk score + 15% keyword match
        rerank_score = (
            0.50 * max_sentence_sim
            + 0.35 * item["bi_encoder_score"]
            + 0.15 * keyword_overlap
        )

        reranked.append(
            {
                **item,
                "titan_max_sentence_sim": round(max_sentence_sim, 4),
                "keyword_overlap": round(keyword_overlap, 4),
                "rerank_score": round(rerank_score, 4),
            }
        )

    # Sort descending by the new rerank_score
    reranked.sort(key=lambda x: x["rerank_score"], reverse=True)

    # Assign new final rank
    for new_rank, item in enumerate(reranked, start=1):
        item["final_rank"] = new_rank

    return reranked


# ==============================================================================
# STEP 6: GROUNDED ANSWER GENERATION WITH STRANDS AGENT ON BEDROCK
# ==============================================================================
def generate_rag_answer(query: str, reranked_chunks: list[dict], top_n: int = 3) -> str:
    """
    Pass the top reranked chunks as context to a Bedrock Strands Agent to
    produce a grounded answer.
    """
    top_context = "\n\n---\n\n".join(
        f"[Rank #{c['final_rank']} | {c['chunk_id']} | Score: {c['rerank_score']}]\n{c['text']}"
        for c in reranked_chunks[:top_n]
    )

    agent = Agent(
        model=BedrockModel(model_id=MODEL_ID),
        system_prompt=(
            "You are an enterprise technical assistant for Acme Cloud Platform. "
            "Answer the user's question strictly using the provided RAG context chunks. "
            "Cite the chunk IDs (e.g., [chunk_03]) that support your answer."
        ),
        callback_handler=None,
    )

    prompt = (
        f"Retrieved & Reranked Context:\n{top_context}\n\n"
        f"User Question: {query}\n\n"
        "Provide a clear, concise answer based only on the context above."
    )
    return str(agent(prompt))


# ==============================================================================
# MAIN EXECUTION DEMO
# ==============================================================================
def main():
    print("=" * 80)
    print("DEMO 8: RAG PIPELINE (CHUNKING -> TITAN EMBEDDINGS -> CHROMADB -> TOP 5 -> RERANK)")
    print("=" * 80)

    # 1. Load and chunk the sample text file
    raw_text = SAMPLE_TEXT_PATH.read_text(encoding="utf-8")
    chunks = chunk_text(raw_text, chunk_size=450, chunk_overlap=75)

    print(f"\n[1. Vector Chunking]")
    print(f"  Source file   : {SAMPLE_TEXT_PATH.name} ({len(raw_text)} characters)")
    print(f"  Chunk config  : chunk_size=450 chars, chunk_overlap=75 chars")
    print(f"  Total chunks  : {len(chunks)} overlapping chunks created")
    print(f"  Sample chunk  : [{chunks[0]['id']}] {chunks[0]['text'][:90]}...")

    # 2. Initialize AWS Titan Embeddings V2 and demonstrate a vector embedding
    titan_ef = TitanEmbeddingFunction(
        model_id=TITAN_EMBED_MODEL_ID,
        region_name=AWS_REGION,
        dimensions=512,
    )
    sample_vector = titan_ef.embed_single(chunks[0]["text"])

    print(f"\n[2. AWS Titan Embeddings]")
    print(f"  Embedding Model : {TITAN_EMBED_MODEL_ID}")
    print(f"  Vector Dimension: {len(sample_vector)} floats per chunk")
    print(f"  First 5 values  : {[round(v, 5) for v in sample_vector[:5]]}")

    # 3. Store chunks & embeddings in ChromaDB
    print(f"\n[3. Storing in ChromaDB]")
    collection = build_chroma_vector_store(chunks, titan_ef)
    print(f"  Collection 'acme_cloud_handbook' indexed with {collection.count()} chunks.")

    # 4. Query ChromaDB for Top 5 candidate answers
    query = (
        "What happens to customer databases and ChromaDB vector collections "
        "after an account is canceled, and when can I get a full refund?"
    )
    print(f"\n[4. Retrieving Top 5 Answers from ChromaDB]")
    print(f"  Query: \"{query}\"\n")

    top_5_candidates = retrieve_top_k(collection, query, top_k=5)
    for c in top_5_candidates:
        preview = c["text"].replace("\n", " ")[:85]
        print(
            f"  Initial #{c['initial_rank']} | {c['chunk_id']} "
            f"| Bi-Encoder Cosine Sim: {c['bi_encoder_score']:.4f} | {preview}..."
        )

    # 5. Rerank the Top 5 candidates using Titan fine-grained sentence embeddings
    print(f"\n[5. Reranking Top 5 Candidates with AWS Titan Embeddings]")
    reranked_top_5 = rerank_with_titan(query, top_5_candidates, titan_ef)
    for c in reranked_top_5:
        preview = c["text"].replace("\n", " ")[:75]
        rank_shift = c["initial_rank"] - c["final_rank"]
        shift_label = (
            f"(+{rank_shift} up)"
            if rank_shift > 0
            else (f"({rank_shift} down)" if rank_shift < 0 else "(unchanged)")
        )
        print(
            f"  Final #{c['final_rank']} {shift_label:11s} | {c['chunk_id']} "
            f"| Rerank: {c['rerank_score']:.4f} "
            f"(SentMaxSim={c['titan_max_sentence_sim']:.4f}, "
            f"ChunkSim={c['bi_encoder_score']:.4f}, "
            f"KW={c['keyword_overlap']:.2f}) | {preview}..."
        )

    # 6. Generate final grounded answer using Top 3 reranked chunks
    print(f"\n[6. Grounded Answer from Strands Agent ({MODEL_ID})]")
    answer = generate_rag_answer(query, reranked_top_5, top_n=3)
    print(answer)


if __name__ == "__main__":
    main()

