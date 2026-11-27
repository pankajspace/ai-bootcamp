"""
Section 10 — BM25 and Reciprocal Rank Fusion from scratch (no API key, no libraries)
===================================================================================
Hybrid search = two ranked lists (meaning search + keyword search) merged into one.
This script builds the keyword side (BM25) and the merge (RRF) by hand, so you can
see every number. It runs instantly and costs nothing.

How to run
----------
    python step01_rrf_by_hand.py

It reads the three documents in ./data, splits them into paragraphs, ranks them with
BM25 for the compliance question, fuses that list with a dense (meaning) ranking, and
shows why we fuse RANKS instead of adding raw SCORES.
"""

import math
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def tokenize(text: str) -> list[str]:
    """Lower-case words and numbers: 'Quick ratio was 1.18.' → ['quick','ratio','was','1.18']"""
    return re.findall(r"[a-z0-9]+(?:\.[0-9]+)?", text.lower())


def bm25_scores(query: str, docs: list[str], k1: float = 1.5, b: float = 0.75) -> list[float]:
    """Score every doc for the query with BM25.

    For each query word:
        idf  = how RARE the word is across all docs   (rare words matter more)
        tf   = how often it appears in THIS doc       (more is better, but saturates)
        norm = penalty for long docs                  (long docs aren't better by default)
    score = Σ idf × tf×(k1+1) / (tf + k1×norm)
    """
    tokenized = [tokenize(d) for d in docs]
    n_docs = len(docs)
    avg_len = sum(len(t) for t in tokenized) / n_docs
    scores = []
    for words in tokenized:
        score = 0.0
        for term in set(tokenize(query)):
            n_with_term = sum(1 for t in tokenized if term in t)
            if n_with_term == 0:
                continue
            idf = math.log(1 + (n_docs - n_with_term + 0.5) / (n_with_term + 0.5))
            tf = words.count(term)
            norm = 1 - b + b * len(words) / avg_len           # = 1 for an average-length doc
            score += idf * tf * (k1 + 1) / (tf + k1 * norm)
        scores.append(score)
    return scores

def rank_ids(scores: list[float]) -> list[int]:
    """Doc ids ordered best → worst (only docs with a positive score)."""
    return [i for i in sorted(range(len(scores)), key=lambda i: -scores[i]) if scores[i] > 0]


def rrf(ranked_lists: list[list[int]], k: int = 60) -> dict[int, float]:
    """Reciprocal Rank Fusion. Each list gives a doc 1/(k + rank), rank starting at 0.

    Raw scores are ignored completely — only POSITIONS count. So a BM25 score of 9.7
    and a cosine of 0.41 can be merged fairly. Appearing in BOTH lists beats topping one.
    """
    fused: dict[int, float] = {}
    for ranking in ranked_lists:
        for rank, doc_id in enumerate(ranking):
            fused[doc_id] = fused.get(doc_id, 0.0) + 1.0 / (k + rank)
    return dict(sorted(fused.items(), key=lambda kv: -kv[1]))

def load_paragraphs() -> list[tuple[str, str]]:
    """(file name, paragraph) for every non-heading paragraph in ./data."""
    out = []
    for path in sorted(DATA_DIR.glob("*.md")):
        for para in path.read_text(encoding="utf-8").split("\n\n"):
            if para.strip() and not para.startswith("#"):
                out.append((path.name, " ".join(para.split())))
    return out


def find(paras, needle: str) -> int:
    return next(i for i, (_, p) in enumerate(paras) if needle in p)


if __name__ == "__main__":
    paras = load_paragraphs()
    texts = [p for _, p in paras]
    question = "Does Acme's Q3 quick ratio satisfy the firm's risk policy?"

    # 1) Keyword side: BM25 over every paragraph
    bm25 = bm25_scores(question, texts)
    bm25_rank = rank_ids(bm25)[:5]

    # 2) Meaning side: in the full lab this list comes from the vector index.
    #    Here we write down a typical dense ranking so the script needs no API key:
    #    embeddings match MEANING, so the paragraph about "liquidity" and "inventory
    #    build" ranks high even though it never says "risk policy".
    dense_rank = [find(paras, "quick ratio at quarter-end"),
                  find(paras, "2.1 Quick ratio"),
                  find(paras, "Should investors worry about liquidity"),
                  find(paras, "2.4 Source of figures"),
                  find(paras, "Excluding inventories")]

    print(f"Question: {question}\n")
    print("BM25 top 5 (keyword match):")
    for r, i in enumerate(bm25_rank):
        print(f"  rank {r}  score {bm25[i]:5.2f}  {paras[i][0]:<26} {texts[i][:55]}…")
    print("\nDense top 5 (meaning match):")
    for r, i in enumerate(dense_rank):
        print(f"  rank {r}               {paras[i][0]:<26} {texts[i][:55]}…")

    # 3) Fuse by rank
    fused = rrf([dense_rank, bm25_rank])
    print("\nRRF fused (k=60):  score = Σ 1/(60 + rank)")
    for i, s in list(fused.items())[:5]:
        where = [name for name, lst in (("dense", dense_rank), ("bm25", bm25_rank)) if i in lst]
        ranks = ", ".join(f"{n}#{(dense_rank if n == 'dense' else bm25_rank).index(i)}" for n in where)
        print(f"  {s:.4f}  [{ranks:<16}] {paras[i][0]:<26} {texts[i][:45]}…")

    # 4) Why not just add the raw scores?
    top_bm25 = bm25[bm25_rank[0]]
    print(f"\nWhy fuse ranks, not scores: a top BM25 score here is {top_bm25:.2f}, while a top")
    print("cosine similarity is usually 0.3–0.8. Adding them lets BM25 drown out meaning search.")
    print(f"1/60 = {1/60:.4f} (1st place in one list)   1/61 + 1/62 = {1/61 + 1/62:.4f} (2nd + 3rd in two lists)")
