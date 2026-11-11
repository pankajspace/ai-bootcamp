"""
Chapter 8 - Reranking: the second, more careful look at the candidates.

Stage 1 (fast, recall):     hybrid search returns ~25-50 candidates.
Stage 2 (slow, precision):  a CROSS-ENCODER reads the query and each candidate TOGETHER
                            and scores how well the candidate answers the query.

A bi-encoder (embedding model) encodes query and chunk separately, so document vectors can
be pre-computed. A cross-encoder must run once per (query, chunk) pair at query time, so we
only use it on a short list.
"""
from __future__ import annotations

import time
import warnings

from .hybrid import Hit


class CrossEncoderReranker:
    def __init__(self, model_name: str = "Xenova/ms-marco-MiniLM-L-6-v2"):
        from fastembed.rerank.cross_encoder import TextCrossEncoder

        self.name = model_name
        self.model = TextCrossEncoder(model_name=model_name)
        self.last_latency_ms = 0.0

    def rerank(self, query: str, hits: list[Hit], top_n: int = 5) -> list[Hit]:
        if not hits:
            return []
        t0 = time.perf_counter()
        scores = list(self.model.rerank(query, [h.chunk.text for h in hits]))
        self.last_latency_ms = (time.perf_counter() - t0) * 1000
        for h, s in zip(hits, scores):
            h.rerank_score = float(s)
        return sorted(hits, key=lambda h: -(h.rerank_score or 0))[:top_n]


class KeywordOverlapReranker:
    """A model-free stand-in used when the cross-encoder cannot be downloaded.
    Combines heading/clause-title intent matching, stemmed content overlap, BM25, and vector similarity."""

    name = "keyword-overlap (fallback)"
    last_latency_ms = 0.0

    @staticmethod
    def _stems(text: str, keep_question_words: bool = False) -> set[str]:
        import re
        from .bm25 import STOPWORDS
        from .embeddings import HashingEmbedder

        q_words = {"who", "where", "when", "how"}
        raw = re.findall(r"[a-z0-9]+", text.lower())
        out = set()
        for w in raw:
            if w in STOPWORDS and not (keep_question_words and w in q_words):
                continue
            out.add(w)
            out.add(HashingEmbedder._stem(w))
        return out

    def rerank(self, query: str, hits: list[Hit], top_n: int = 5) -> list[Hit]:
        if not hits:
            return []
        q_content = self._stems(query, keep_question_words=False)
        q_with_intent = self._stems(query, keep_question_words=True)
        max_bm = max((h.bm25_score or 0.0) for h in hits) or 1.0
        for h in hits:
            heading = str(h.chunk.metadata.get("heading", "")) + " " + str(h.chunk.metadata.get("section", ""))
            head_stems = self._stems(heading, keep_question_words=True)
            body_stems = self._stems(h.chunk.text, keep_question_words=False)

            body_cov = len(q_content & body_stems) / max(1, len(q_content))
            head_cov = len(q_with_intent & head_stems) / max(1, len(q_with_intent))
            # Direct phrase/intent match in clause heading (e.g. "Who approves" -> "AI-5.1 Who approves")
            head_exact = 0.35 if len(q_with_intent & head_stems) >= 2 else 0.0
            bm_norm = (h.bm25_score or 0.0) / max_bm
            vec_sim = max(0.0, h.vector_score or 0.0)
            rrf_s = h.score or 0.0

            h.rerank_score = (
                2.5 * body_cov
                + 1.8 * head_cov
                + head_exact
                + 1.2 * bm_norm
                + 0.8 * vec_sim
                + 5.0 * rrf_s
            )
        return sorted(hits, key=lambda h: -(h.rerank_score or 0))[:top_n]


def get_reranker(model_name: str | None = None):
    from .config import get_settings

    name = model_name or get_settings().reranker_model
    try:
        return CrossEncoderReranker(name)
    except Exception:
        return KeywordOverlapReranker()
