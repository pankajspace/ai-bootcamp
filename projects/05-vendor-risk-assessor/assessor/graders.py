"""
graders.py — the two checks before an answer leaves the system.

COURSE MAP
  Agentic RAG guide  "agents.py → Answer Grader" (is the retrieved text relevant to the question?) and
                     "Hallucination Grader" (is every statement in the answer supported by the sources?).
  Production RAG     Module 9 "Reasoning, self-checks and guardrails"; Module 10 "Answer metrics" (faithfulness).

Milestone 3:
  * Ports the Answer Grader and Hallucination Grader agent personas and task prompts from `02-agentic-rag`.
  * Calls both graders through `LLM.small.structured(..., GradeResult)`.
  * Wires a bounded retry loop in `grade_policy_answer()`:
      - `relevant=False` → broaden the policy search once (`k=8` + query expansion) and re-answer.
      - `grounded=False` → regenerate once with a stricter prompt (`STRICT_REGEN_SYSTEM`), re-grade, and if still
        ungrounded, abstain (`pa.abstained = True`).
"""

from __future__ import annotations

import re
from typing import Any, Callable, Iterable, Optional

from pydantic import BaseModel

from .llm import LLM
from .policy_rag import tokenize
from .schemas import PolicyAnswer

ABSTAIN_UNGROUNDED_MSG = (
    "I found related policy text but could not produce an answer that is fully supported by it. "
    "Please read the cited clauses directly."
)


class GradeResult(BaseModel):
    verdict: bool
    reason: str = ""


# Ported from 02-agentic-rag/code/agents.py & tasks.py (Answer Grader & Hallucination Grader)
ANSWER_GRADER_ROLE = "Answer Relevance & Utility Grader"
ANSWER_GRADER_GOAL = (
    "Filter out retrieved policy passages that do not actually answer the user's question, "
    "and trigger a broader policy search when retrieval falls short."
)
ANSWER_GRADER_BACKSTORY = (
    "You are a meticulous quality assurance specialist who evaluates whether retrieved policy clauses "
    "contain the specific facts needed to answer a compliance question. Related topic alone is not enough."
)

HALLUCINATION_GRADER_ROLE = "Groundedness & Hallucination Auditor"
HALLUCINATION_GRADER_GOAL = (
    "Ensure 100% faithfulness by verifying that every claim, number, role, and clause ID in the draft answer "
    "is directly supported by the retrieved policy sources."
)
HALLUCINATION_GRADER_BACKSTORY = (
    "You are a strict compliance auditor who never tolerates speculation, fabricated policy clauses, "
    "or extrapolated rules. If any statement or cited clause ID goes beyond the source text, you fail it."
)

RELEVANCE_SYSTEM = f"""Role: {ANSWER_GRADER_ROLE}
Goal: {ANSWER_GRADER_GOAL}
Backstory: {ANSWER_GRADER_BACKSTORY}

Given a user question and retrieved policy text, decide whether the retrieved text contains the specific information
needed to answer the question. Be strict: sharing a broad topic is not enough.
Return JSON: {{"verdict": true|false, "reason": "one-sentence explanation"}}."""

GROUNDED_SYSTEM = f"""Role: {HALLUCINATION_GRADER_ROLE}
Goal: {HALLUCINATION_GRADER_GOAL}
Backstory: {HALLUCINATION_GRADER_BACKSTORY}

Given retrieved policy sources and a draft answer, verify that EVERY factual statement, number, role, and cited clause ID
in the answer is directly supported by the sources. If any statement or clause ID is fabricated or unsupported, verdict is false.
Return JSON: {{"verdict": true|false, "reason": "one-sentence explanation"}}."""

STRICT_REGEN_SYSTEM = """You are NovaMind's strict policy compliance writer.
Your previous draft contained statements not fully supported by the retrieved policy clauses.
Rewrite the answer using ONLY verbatim facts and exact clause IDs from the provided policy text.
Do NOT invent clause IDs, numbers, timelines, or roles. If the policy text does not support an answer, reply with 'ABSTAIN'."""

_CLAUSE_ID_RE = re.compile(r"\b(?:AI|SEC|DP|PROC|AVL|CRYPTO|IR)-\d+(?:\.\d+)?\b")


def expand_policy_query(question: str, llm: Optional[LLM] = None) -> str:
    """Broaden a policy query with domain synonyms when initial k=4 retrieval was graded irrelevant."""
    q_low = question.lower()
    expansions: list[str] = [question]
    synonym_map = {
        "approve": "approval sign-off governance reviewer tier",
        "sign off": "approval reviewer authority tier DPO",
        "store": "residency hosting region India EU DP-3",
        "breach": "incident notification CERT-In 6 hours 72 hours IR-2",
        "key": "cryptography KMS rotation AES-256 TLS CRYPTO",
        "encrypt": "encryption TLS AES-256 KMS CRYPTO",
        "train": "model training fine-tuning customer data AI-3.1",
        "retain": "retention deletion 30 days 90 days DP-4",
    }
    for trigger, extra in synonym_map.items():
        if trigger in q_low:
            expansions.append(extra)
    return " ".join(expansions)


def grade_relevance(question: str, context: str, llm: Optional[LLM] = None) -> GradeResult:
    def mock() -> dict:
        if not context.strip():
            return {"verdict": False, "reason": "empty context (heuristic)"}
        q, c = set(tokenize(question)), set(tokenize(context))
        if not q:
            return {"verdict": False, "reason": "empty question tokens (heuristic)"}
        overlap = len(q & c)
        needed = max(1, len(q) // 3)
        return {
            "verdict": overlap >= needed,
            "reason": f"{overlap}/{len(q)} question terms found in context (heuristic)",
        }

    client = (llm or LLM()).small()
    return client.structured(
        RELEVANCE_SYSTEM,
        f"Question: {question}\n\nContext:\n{context[:6000]}",
        GradeResult,
        stage="grade_relevance",
        mock=mock,
    )


def grade_grounded(answer: str, sources: str, llm: Optional[LLM] = None) -> GradeResult:
    def mock() -> dict:
        if not answer.strip() or not sources.strip():
            return {"verdict": False, "reason": "empty answer or sources (heuristic)"}

        # 1. Check for fabricated clause IDs (e.g., citing SEC-99.9 when it does not appear in sources).
        src_clauses = set(_CLAUSE_ID_RE.findall(sources))
        ans_clauses = _CLAUSE_ID_RE.findall(answer)
        body_without_prefix = re.sub(r"^[A-Z]{1,6}-[\d.]+:\s*", "", answer)
        inline_clauses = _CLAUSE_ID_RE.findall(body_without_prefix)

        if src_clauses:
            fabricated = [cid for cid in ans_clauses if cid not in src_clauses]
            if fabricated:
                return {"verdict": False, "reason": f"fabricated clause ID not in sources: {fabricated[0]} (heuristic)"}
        elif inline_clauses:
            # Sources had no clause headers passed in, but the answer body invented an inline clause reference
            for cid in inline_clauses:
                if cid.lower() not in sources.lower():
                    return {"verdict": False, "reason": f"fabricated inline clause ID: {cid} (heuristic)"}

        # 2. Every sentence of the answer must share >= 60% of its content words with the sources.
        src = set(tokenize(sources))
        body = re.sub(r"^[A-Z]{1,6}-[\d.]+:\s*", "", answer)
        body = re.sub(r"\(source:.*?\)\s*$", "", body).strip()
        sentences = [s for s in re.split(r"(?<=[.!?])\s+|\s*\|\s*", body) if len(tokenize(s)) >= 3]
        if not sentences and len(tokenize(body)) > 0:
            sentences = [body]
        unsupported = [
            s for s in sentences
            if len(set(tokenize(s)) & src) / max(1, len(set(tokenize(s)))) < 0.6
        ]
        return {
            "verdict": not unsupported,
            "reason": ("all sentences supported" if not unsupported else f"unsupported: {unsupported[0][:80]}") + " (heuristic)",
        }

    client = (llm or LLM()).small()
    return client.structured(
        GROUNDED_SYSTEM,
        f"Sources:\n{sources[:8000]}\n\nAnswer:\n{answer}",
        GradeResult,
        stage="grade_grounded",
        mock=mock,
    )


def _format_citations_context(pa: PolicyAnswer) -> str:
    blocks: list[str] = []
    for h in pa.citations:
        header = f"[{h.clause_id or h.heading} | {h.title} | v{h.version}]"
        blocks.append(f"{header}\n{h.text}")
    return "\n\n".join(blocks)


def grade_policy_answer(
    pa: PolicyAnswer,
    llm: Optional[LLM] = None,
    *,
    library: Any = None,
    user_groups: Iterable[str] = ("public", "employees"),
    strict_regenerator: Optional[Callable[[PolicyAnswer, str], str]] = None,
) -> PolicyAnswer:
    """Grade a PolicyAnswer for relevance and groundedness, with bounded M3 retry loops:
    1. If `relevant=False` and `library` is available: expand the query and broaden search (`k=8`) once.
    2. If `grounded=False`: attempt one strict regeneration (`STRICT_REGEN_SYSTEM` or `strict_regenerator`),
       re-grade, and if still ungrounded, abstain (`pa.abstained = True`).
    """
    if pa.abstained or not pa.citations:
        return pa

    active_llm = llm or LLM()
    ctx = _format_citations_context(pa)

    # --- Step 1: Answer Grader (Relevance) + Broaden Search Retry ---
    pa.grader_relevant = grade_relevance(pa.question, ctx, active_llm).verdict
    if not pa.grader_relevant and library is not None:
        expanded_q = expand_policy_query(pa.question, active_llm)
        broadened_hits = library.search(expanded_q, user_groups, k=8)
        if broadened_hits and broadened_hits[0].score >= library.ABSTAIN_BELOW:
            # Re-answer with broadened k=8 context if the original answer came from library
            retry_pa = library.answer(expanded_q, user_groups, llm=active_llm, k=8)
            if not retry_pa.abstained and retry_pa.citations:
                pa.citations = retry_pa.citations
                pa.answer = retry_pa.answer
                ctx = _format_citations_context(pa)
                pa.grader_relevant = grade_relevance(pa.question, ctx, active_llm).verdict

    # --- Step 2: Hallucination Grader (Groundedness) + Strict Regeneration Retry ---
    pa.grader_grounded = grade_grounded(pa.answer, ctx, active_llm).verdict
    if not pa.grader_grounded:
        regenerated: Optional[str] = None
        if strict_regenerator is not None:
            regenerated = strict_regenerator(pa, ctx)
        elif not active_llm.mock_mode:
            try:
                draft = active_llm.text(
                    STRICT_REGEN_SYSTEM,
                    f"Question: {pa.question}\n\nPolicy Clauses:\n{ctx}\n\nPrevious Draft:\n{pa.answer}",
                    stage="policy_strict_regen",
                ).strip()
                if draft and "ABSTAIN" not in draft.upper():
                    regenerated = draft
            except Exception:
                regenerated = None

        if regenerated:
            pa.answer = regenerated
            pa.grader_grounded = grade_grounded(pa.answer, ctx, active_llm).verdict

        if not pa.grader_grounded:
            pa.abstained = True
            pa.answer = ABSTAIN_UNGROUNDED_MSG

    return pa

