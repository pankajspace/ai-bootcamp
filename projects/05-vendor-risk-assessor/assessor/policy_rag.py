"""
policy_rag.py — the internal policy library: Nimbu Mart's own documents, searched with access control.

COURSE MAP
  Production RAG course  Module 6  (chunking: we chunk by clause heading so every hit has a clause id)
                         Module 8  (retrieval: hybrid BM25 + vectors with RRF + cross-encoder/intent reranker)
                         Module 9  (grounded generation: LLM grounded answers with citations + extractive fallback; refuse when weak)
                         Module 11 (security: ACL lives IN retrieval; archived, draft, untrusted, and injected docs filtered)
                         Module 13 (the production app)
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

from rag_core.documents import Chunk, stable_chunk_id
from rag_core.embeddings import HashingEmbedder, get_embedder
from rag_core.hybrid import HybridRetriever
from rag_core.rerank import get_reranker
from rag_core.security import acl_filter, detect_injection

from .config import POLICY_DIR
from .schemas import PolicyAnswer, PolicyHit

STOPWORDS = set("""a an and are as at be by for from has have how if in is it its of on or our that the this to was we what
when where which who will with you your must may can does do did into than then there these those also any all not no
according say says said""".split())

_CLAUSE_RE = re.compile(r"^([A-Z]{1,5}(?:-[\dA-Z]+)+(?:\.\d+)*)\b\s*(.*)$")  # SEC-4.2, AVL-1, Q-SEC-4.2, DP-3.1-DRAFT


def tokenize(text: str) -> list[str]:
    text = text.lower()
    # keep clause ids like sec-4.2 as single tokens too
    ids = re.findall(r"\b[a-z]{1,5}-\d+(?:\.\d+)*(?:-[a-z0-9]+)?\b", text)
    words = re.findall(r"[a-z0-9]+", text)
    base = [w for w in words if w not in STOPWORDS and len(w) > 1]
    stems = [HashingEmbedder._stem(w) for w in base]
    # Preserve base words first, plus stems (deduplicated per token if identical) and clause ids
    out = list(base)
    for w, st in zip(base, stems):
        if st != w:
            out.append(st)
    return out + ids


@dataclass
class PolicyChunk:
    doc: str
    title: str
    doc_id: str
    clause_id: str
    heading: str
    text: str
    version: str
    status: str
    trust: str
    access: list[str]
    effective_date: str = ""
    section: str = ""
    injected: bool = False
    tokens: list[str] = field(default_factory=list)


def chunk_markdown(doc: str, text: str, meta: dict) -> list[PolicyChunk]:
    """One chunk per `###` clause (or per `##` section when a section has no clauses).

    Production RAG course Module 6, "Structure-aware chunking": headings are the natural unit of a
    policy. Each chunk keeps its clause id so a citation can say "SEC-4.2", not "chunk 17".
    """
    chunks: list[PolicyChunk] = []
    section = ""
    cur_head, cur_lines, cur_clause = "", [], ""

    def flush():
        body = "\n".join(l for l in cur_lines).strip()
        if body:
            head = cur_head or section or meta.get("title", doc)
            inj = bool(detect_injection(body))
            chunks.append(PolicyChunk(
                doc=doc, title=meta.get("title", doc), doc_id=meta.get("doc_id", ""), clause_id=cur_clause,
                heading=head, text=body, version=str(meta.get("version", "")), status=meta.get("status", "active"),
                trust=meta.get("trust", "trusted"), access=list(meta.get("access", ["public"])),
                effective_date=str(meta.get("effective_date", "")), section=section, injected=inj,
                tokens=tokenize(f"{section} {head} {body}")))

    for line in text.splitlines():
        if line.startswith("### "):
            flush()
            cur_lines = []
            raw = line[4:].strip()
            m = _CLAUSE_RE.match(raw)
            cur_clause, cur_head = (m.group(1), raw) if m else ("", raw)
        elif line.startswith("## "):
            flush()
            cur_lines, cur_clause, cur_head = [], "", ""
            section = line[3:].strip()
        elif line.startswith("# "):
            flush()
            cur_lines, cur_clause, cur_head = [], "", ""
        else:
            cur_lines.append(line)
    flush()
    return chunks


class BM25:
    """Minimal BM25 (Production RAG Module 8, "Hybrid search: keywords + meaning" — this is the keyword half)."""

    def __init__(self, docs: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.docs = docs
        self.n = len(docs)
        self.avgdl = sum(len(d) for d in docs) / max(1, self.n)
        self.df: Counter = Counter()
        for d in docs:
            self.df.update(set(d))
        self.tf = [Counter(d) for d in docs]

    def idf(self, term: str) -> float:
        df = self.df.get(term, 0)
        return math.log((self.n - df + 0.5) / (df + 0.5) + 1.0)

    def score(self, query: list[str], idx: int) -> float:
        tf, dl = self.tf[idx], len(self.docs[idx])
        s = 0.0
        for q in query:
            f = tf.get(q, 0)
            if not f:
                continue
            s += self.idf(q) * (f * (self.k1 + 1)) / (f + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
        return s


GROUNDED_POLICY_SYSTEM = """You are Nimbu Mart's internal policy assistant.
Answer the user's question ONLY using the provided policy clauses.
Rules:
1. Cite the exact clause ID (e.g. DP-3.1, SEC-4.2, AI-5.1) and document version (e.g. v2026.1) in your answer.
2. Never invent policy rules or cite documents not in the context.
3. If the provided clauses do not answer the question, reply with exactly: ABSTAIN"""


class PolicyLibrary:
    ABSTAIN_BELOW = 2.0  # Combined hybrid + rerank score threshold; tuned with eval/run_eval.py

    def __init__(self, policy_dir: Path = POLICY_DIR, embedder_kind: str = "hashing", use_reranker: bool = True):
        self.policy_dir = Path(policy_dir)
        self.use_reranker = use_reranker
        self.meta: dict = json.loads((self.policy_dir / "_metadata.json").read_text(encoding="utf-8"))
        self.chunks: list[PolicyChunk] = []
        for name, m in self.meta.items():
            if name.startswith("_"):
                continue
            p = self.policy_dir / name
            if not p.exists():
                continue
            self.chunks.extend(chunk_markdown(name, p.read_text(encoding="utf-8"), m))
        self.bm25 = BM25([c.tokens for c in self.chunks])

        # Build rag_core Chunk objects with full metadata and index them in HybridRetriever
        self._chunk_by_id: dict[str, tuple[int, PolicyChunk]] = {}
        rag_chunks: list[Chunk] = []
        for idx, c in enumerate(self.chunks):
            cid = stable_chunk_id(c.doc, c.version, idx, c.heading + "\n" + c.text)
            self._chunk_by_id[cid] = (idx, c)
            full_text = f"{c.heading} ({c.section})\n{c.text}" if c.section and c.section != c.heading else f"{c.heading}\n{c.text}"
            rag_chunks.append(Chunk(
                chunk_id=cid,
                doc_id=c.doc_id or c.doc,
                text=full_text,
                metadata={
                    "doc": c.doc,
                    "title": c.title,
                    "doc_id": c.doc_id,
                    "clause_id": c.clause_id,
                    "heading": c.heading,
                    "section": c.section,
                    "version": c.version,
                    "status": c.status,
                    "trust": c.trust,
                    "access": list(c.access),
                    "effective_date": c.effective_date,
                    "injected": c.injected,
                },
            ))
        self.embedder = get_embedder(embedder_kind)
        self.retriever = HybridRetriever(self.embedder, rag_chunks)
        self.reranker = get_reranker()

    # ------------------------------------------------------------------ filters
    @staticmethod
    def _allowed(chunk: PolicyChunk, user_groups: Iterable[str]) -> bool:
        groups = set(user_groups) | {"public"}
        return bool(groups & set(chunk.access))

    def search(self, question: str, user_groups: Iterable[str] = ("public",), *, k: int = 5,
               include_archived: bool = False, include_draft: bool = False,
               trusted_only: bool = True, use_reranker: Optional[bool] = None) -> list[PolicyHit]:
        """Filter FIRST (ACL, archived/draft, trust, injection), then hybrid retrieve (BM25 + vectors, RRF) + rerank."""
        groups = list(set(user_groups) | {"public"})
        allowed_statuses = ["active"]
        if include_archived:
            allowed_statuses.append("archived")
        if include_draft:
            allowed_statuses.append("draft")

        where: dict = {
            **acl_filter(groups),
            "status": {"$in": allowed_statuses},
        }
        if trusted_only:
            where["trust"] = "trusted"
            where["injected"] = False

        q_tokens = tokenize(question)
        if not q_tokens:
            return []

        raw_hits = self.retriever.retrieve(question, k=max(k * 4, 25), mode="hybrid", where=where, candidates=40)
        # Keep only hits that have positive lexical/stem match so unrelated queries (e.g. biryani) don't match via hash collisions
        filtered_hits = []
        for h in raw_hits:
            idx, pc = self._chunk_by_id[h.chunk.chunk_id]
            bm_s = self.bm25.score(q_tokens, idx)
            h.bm25_score = bm_s
            if bm_s > 0 or (pc.clause_id and pc.clause_id.lower() in question.lower()):
                filtered_hits.append(h)

        if not filtered_hits:
            return []

        do_rerank = self.use_reranker if use_reranker is None else use_reranker
        if do_rerank:
            reranked = self.reranker.rerank(question, filtered_hits, top_n=len(filtered_hits))
        else:
            reranked = filtered_hits

        out: list[PolicyHit] = []
        q_low = question.lower()
        for h in reranked:
            idx, c = self._chunk_by_id[h.chunk.chunk_id]
            base_bm = h.bm25_score if h.bm25_score is not None else self.bm25.score(q_tokens, idx)
            # Combine rerank score and BM25 score on a consistent scale (>= 2.0 when relevant)
            rerank_val = (h.rerank_score if h.rerank_score is not None else (h.score * 30.0))
            combined = 0.65 * rerank_val + 0.35 * base_bm
            if c.clause_id and c.clause_id.lower() in q_low:
                combined += 5.0  # hard boost when user names the exact clause
            if combined <= 0:
                continue
            out.append(PolicyHit(
                doc=c.doc, title=c.title, doc_id=c.doc_id, clause_id=c.clause_id, heading=c.heading,
                text=c.text, score=round(combined, 3), version=c.version, status=c.status, trust=c.trust,
                access=c.access
            ))
        out.sort(key=lambda x: -x.score)
        return out[:k]

    # ------------------------------------------------------------------ answers
    @staticmethod
    def _sentences(text: str) -> list[str]:
        """Split a markdown chunk into citable units: sentences, list items, table rows."""
        parts: list[str] = []
        buf: list[str] = []

        def flush():
            if buf:
                para = " ".join(buf)
                parts.extend(s.strip() for s in re.split(r"(?<=[.!?])\s+", para) if s.strip())
                buf.clear()

        lines = [l.strip() for l in text.splitlines()]
        for i, line in enumerate(lines):
            if not line or set(line) <= set("|-: "):
                flush()
                continue
            if line.startswith("|"):
                flush()
                is_header = i + 1 < len(lines) and lines[i + 1].startswith("|") and set(lines[i + 1]) <= set("|-: ")
                if not is_header:
                    parts.append(line)
            elif line.startswith(("- ", "* ")) or re.match(r"^\d+\.\s", line):
                flush()
                buf.append(line.lstrip("-* "))
            else:
                buf.append(line)
        flush()
        return parts

    def answer(self, question: str, user_groups: Iterable[str] = ("public",), *, llm=None, k: int = 4,
               include_archived: bool = False, include_draft: bool = False) -> PolicyAnswer:
        hits = self.search(question, user_groups, k=k, include_archived=include_archived, include_draft=include_draft)
        if not hits or hits[0].score < self.ABSTAIN_BELOW:
            return PolicyAnswer(question=question, abstained=True, citations=hits[:2],
                                answer="I could not find this in the policy documents you have access to. "
                                       "If it concerns the Approved Vendor List, ask Procurement.")

        if llm is not None and not llm.mock_mode:
            ctx_blocks = []
            for h in hits[:k]:
                label = h.clause_id or h.heading
                ctx_blocks.append(f"[{label} | {h.title} | v{h.version}]\n{h.text}")
            context_str = "\n\n".join(ctx_blocks)
            try:
                draft = llm.text(
                    GROUNDED_POLICY_SYSTEM,
                    f"Question: {question}\n\nPolicy Clauses:\n{context_str}",
                    stage="policy_answer",
                ).strip()
                if draft and "ABSTAIN" not in draft.upper():
                    from .graders import grade_grounded

                    g = grade_grounded(draft, context_str, llm=llm)
                    if not g.verdict:
                        return PolicyAnswer(
                            question=question,
                            abstained=True,
                            citations=hits,
                            mode="llm",
                            grader_grounded=False,
                            answer="I found related policy text but could not produce an answer that is fully supported by it. Please read the cited clauses directly.",
                        )
                    top = hits[0]
                    label = top.clause_id or top.heading
                    if f"v{top.version}" not in draft:
                        draft = f"{draft}  (source: {top.title}, v{top.version})"
                    if label not in draft:
                        draft = f"{label}: {draft}"
                    return PolicyAnswer(question=question, answer=draft, citations=hits, mode="llm", grader_grounded=True)
            except Exception:
                pass  # Fall back to extractive answer if live LLM call fails

        # Extractive mode: the best-matching sentences of the top chunk, prefixed by its clause id.
        q = set(tokenize(question))
        top = hits[0]
        scored = sorted(((len(q & set(tokenize(s))), -i, s) for i, s in enumerate(self._sentences(top.text))), reverse=True)
        best = [s for n, _, s in scored[:2] if n > 0] or [self._sentences(top.text)[0]]
        label = top.clause_id or top.heading
        text = f"{label}: " + " ".join(best) + f"  (source: {top.title}, v{top.version})"
        return PolicyAnswer(question=question, answer=text, citations=hits, mode="extractive")

    # ------------------------------------------------------------------ the Approved Vendor List
    def approved_vendor_entry(self, vendor: str, user_groups: Iterable[str]) -> dict | str | None:
        """Look the vendor up in the restricted Approved Vendor List.

        Returns a dict {status, tier, plan, approved_on, notes}, None if the vendor is not listed,
        or the string "NO_ACCESS" when the caller's groups may not see the list. The matcher turns
        NO_ACCESS into UNKNOWN — the assistant must never leak the list to people without access.
        """
        avl = [c for c in self.chunks if c.doc_id == "NM-PROC-AVL"]
        if not avl:
            return None
        if not any(self._allowed(c, user_groups) for c in avl):
            return "NO_ACCESS"
        v = vendor.lower()
        for c in avl:
            status = {"AVL-1": "approved", "AVL-2": "in_progress", "AVL-3": "rejected"}.get(c.clause_id, "")
            for line in c.text.splitlines():
                if not line.startswith("|") or set(line) <= set("|-: "):
                    continue
                cells = [x.strip() for x in line.strip("|").split("|")]
                if len(cells) < 2 or cells[0].lower() in ("vendor",):
                    continue
                if v in cells[0].lower() or v in cells[1].lower():
                    if status == "approved" and len(cells) >= 7:
                        tier = cells[2].split()[0] if cells[2] else ""
                        return {"status": status, "tier": tier, "plan": cells[3], "approved_on": cells[4],
                                "next_review": cells[5], "notes": cells[6]}
                    if status == "in_progress" and len(cells) >= 5:
                        return {"status": status, "requested_tier": cells[2].split()[0], "notes": cells[4]}
                    if status == "rejected" and len(cells) >= 4:
                        return {"status": status, "date": cells[2], "notes": cells[3]}
        return None
