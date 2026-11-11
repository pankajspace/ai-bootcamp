"""
Chapter 7 - Embedding models behind one small interface.

Every embedder has:
    .name, .dim
    .embed_documents(list_of_texts) -> numpy array, shape (n, dim), each row length 1
    .embed_query(text)              -> numpy array, shape (dim,), length 1

Vectors are L2-normalised (length 1). That makes cosine similarity == dot product, and
it gives the SAME ranking as Euclidean distance. (Chapter 8 explains why.)

Backends:
    fastembed  local ONNX models from Qdrant's fastembed (default: BAAI/bge-small-en-v1.5, 384 dims)
    openai     OpenAI text-embedding-3-small / -large (supports shorter vectors via `dimensions`)
    wordllama  tiny model shipped INSIDE the pip package - works with no internet at all
    hashing    a toy keyword hasher with no model: only for tests and for intuition
"""
from __future__ import annotations

import hashlib
import re

import numpy as np

# Some models are trained with special prefixes for queries vs documents.
# Using the wrong (or no) prefix silently lowers retrieval quality.
PREFIXES = {
    "intfloat/multilingual-e5-large": ("query: ", "passage: "),
    "intfloat/e5": ("query: ", "passage: "),
    "nomic-ai/nomic-embed-text-v1.5": ("search_query: ", "search_document: "),
    "nomic-ai/nomic-embed-text-v1.5-Q": ("search_query: ", "search_document: "),
    "nomic-ai/nomic-embed-text-v1": ("search_query: ", "search_document: "),
    # bge v1.5 works without an instruction; BAAI says adding it for short queries can help a little.
    "BAAI/bge-small-en-v1.5": ("", ""),
}


def normalize(vectors: np.ndarray) -> np.ndarray:
    vectors = np.asarray(vectors, dtype=np.float32)
    norms = np.linalg.norm(vectors, axis=-1, keepdims=True)
    return vectors / np.clip(norms, 1e-12, None)


class Embedder:
    name: str = "base"
    dim: int = 0

    def embed_documents(self, texts: list[str]) -> np.ndarray:  # pragma: no cover
        raise NotImplementedError

    def embed_query(self, text: str) -> np.ndarray:
        return self.embed_documents([text])[0]


class FastEmbedEmbedder(Embedder):
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5", threads: int | None = None):
        from fastembed import TextEmbedding

        self.name = model_name
        self.model = TextEmbedding(model_name=model_name, threads=threads)
        self.q_prefix, self.d_prefix = PREFIXES.get(model_name, ("", ""))
        self.dim = len(next(iter(self.model.embed(["probe"]))))

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        return normalize(np.array(list(self.model.embed([self.d_prefix + t for t in texts], batch_size=64))))

    def embed_query(self, text: str) -> np.ndarray:
        return normalize(np.array(list(self.model.embed([self.q_prefix + text]))))[0]


class OpenAIEmbedder(Embedder):
    def __init__(self, model_name: str = "text-embedding-3-small", dimensions: int | None = None):
        from openai import OpenAI

        self.client = OpenAI()
        self.name = model_name
        self.dimensions = dimensions
        self.dim = dimensions or (3072 if "large" in model_name else 1536)

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        out = []
        for i in range(0, len(texts), 256):  # the API accepts batches of inputs
            kwargs = {"model": self.name, "input": texts[i:i + 256]}
            if self.dimensions:
                kwargs["dimensions"] = self.dimensions  # Matryoshka-style shortening
            resp = self.client.embeddings.create(**kwargs)
            out.extend(d.embedding for d in resp.data)
        return normalize(np.array(out)) if out else np.zeros((0, self.dim), dtype=np.float32)


class WordLlamaEmbedder(Embedder):
    """Very small static model (weights come with `pip install wordllama`). Lower quality than
    bge-small, but it needs no download - handy behind strict corporate firewalls."""

    def __init__(self, dim: int = 256):
        import shutil
        from pathlib import Path

        import wordllama
        from wordllama import WordLlama

        # wordllama 0.4 ships its tokenizer in "tokenizers/" but looks for it in "tokenizer/" and
        # then tries to download it. Copy the bundled file into its cache so no download is needed.
        try:
            src = Path(wordllama.__file__).parent / "tokenizers" / "l2_supercat_tokenizer_config.json"
            dst = Path(WordLlama.DEFAULT_CACHE_DIR) / "tokenizers" / src.name
            if src.exists() and not dst.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(src, dst)
        except Exception:
            pass
        self.model = WordLlama.load(dim=dim)
        self.name = f"wordllama-l2-supercat-{dim}"
        self.dim = dim

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        return normalize(self.model.embed(texts))


class HashingEmbedder(Embedder):
    """A dependency-free local embedder: words, stems, bigrams, and 3-4 char n-grams hashed into buckets."""

    _SYNONYMS = {
        "approves": "approve", "approved": "approve", "approver": "approve", "approvers": "approve", "approval": "approve",
        "signoff": "approve", "authorize": "approve",
        "stored": "store", "storage": "store", "residency": "store", "region": "store", "regions": "store", "located": "store",
        "handles": "handle", "handling": "handle", "processes": "handle", "processing": "handle",
        "incidents": "incident", "breach": "incident", "breached": "incident", "outage": "incident",
        "rotated": "rotate", "rotation": "rotate", "rotating": "rotate",
        "notify": "notification", "notified": "notification", "report": "notification", "escalation": "notification",
    }

    def __init__(self, dim: int = 1024):
        self.dim = dim
        self.name = f"hashing-{dim}"

    @classmethod
    def _stem(cls, w: str) -> str:
        if w in cls._SYNONYMS:
            return cls._SYNONYMS[w]
        if len(w) > 5 and w.endswith("ation"):
            return w[:-5]
        if len(w) > 4 and w.endswith("ies"):
            return w[:-3] + "y"
        if len(w) > 4 and w.endswith("ing"):
            return w[:-3]
        if len(w) > 4 and w.endswith("ed"):
            return w[:-2]
        if len(w) > 3 and w.endswith("es"):
            return w[:-2]
        if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            return w[:-1]
        return w

    def _features(self, text: str) -> list[str]:
        words = re.findall(r"[a-z0-9₹]+", text.lower())
        stems = [self._stem(w) for w in words]
        bigrams = [f"{stems[i]}_{stems[i + 1]}" for i in range(len(stems) - 1)]
        grams = [w[i:i + 3] for w in words for i in range(max(1, len(w) - 2))]
        return words + stems + bigrams + grams

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        mat = np.zeros((len(texts), self.dim), dtype=np.float32)
        for row, text in enumerate(texts):
            for feat in self._features(text):
                h = int(hashlib.md5(feat.encode()).hexdigest(), 16)
                mat[row, h % self.dim] += 1.0 if (h >> 64) % 2 == 0 else -1.0
        mat = np.sign(mat) * np.log1p(np.abs(mat))
        return normalize(mat)


def get_embedder(kind: str | None = None, model_name: str | None = None) -> Embedder:
    """Build the embedder chosen in settings (EMBEDDER / EMBED_MODEL in .env), with offline fallback."""
    from .config import get_settings

    s = get_settings()
    kind = (kind or s.embedder).lower()
    if kind == "fastembed":
        try:
            return FastEmbedEmbedder(model_name or s.embed_model)
        except Exception:
            return HashingEmbedder()
    if kind == "openai":
        name = model_name or (s.embed_model if s.embed_model.startswith("text-embedding") else "text-embedding-3-small")
        return OpenAIEmbedder(name)
    if kind == "wordllama":
        try:
            return WordLlamaEmbedder()
        except Exception:
            return HashingEmbedder()
    if kind == "hashing":
        return HashingEmbedder()
    raise ValueError(f"Unknown EMBEDDER={kind!r}. Use fastembed, openai, wordllama or hashing.")


def fingerprint(embedder: Embedder) -> str:
    """A short id for 'which model made these vectors'. Store it next to every vector:
    vectors from two different models must NEVER be mixed in one index."""
    return f"{embedder.name}:{embedder.dim}"
