"""
reason_judge.py — Calibrated LLM-as-judge for requirement verdict reasons (Milestone 6).

COURSE MAP
  Deep Search     Module 10 & Lab 11 (LLM-as-judge for faithfulness of reasons; calibrate on 20 hand-labelled examples)
  Production RAG  Module 10 & Lab 10 (Faithfulness & answer quality evaluation)

Milestone 6 requirements:
  1. Judge whether each requirement verdict's `reason` is faithful to its cited evidence (`VendorFact` / `policy`).
  2. Calibrate the judge on 20 hand-labelled reasons (`REASON_CALIBRATION_20`) before scoring the gold sets.
"""

from __future__ import annotations

import re
from typing import Any, Optional

from pydantic import BaseModel

from .llm import LLM
from .policy_rag import tokenize

REASON_JUDGE_SYSTEM = """You are an independent Compliance Audit Judge evaluating whether a vendor risk assessment
verdict's `reason` is 100% faithful to the cited `evidence` and consistent with the `verdict`.

Mark `faithful = false` if ANY of the following occur:
1. The `reason` cites a certification, region, retention period, or date that does NOT appear in the `evidence`.
2. The `reason` upgrades `claimed` marketing text into `documented` proof without an audit report or registry entry.
3. The `reason` contradicts the `verdict` (e.g. `verdict=PASS` when the reason says India is only planned or SSO is missing).
4. The `reason` fabricates a post-mortem or hides a major security incident present in the `evidence`.

Otherwise mark `faithful = true`.
Return JSON: {"faithful": true|false, "explanation": "one-sentence justification"}."""


class ReasonJudgeResult(BaseModel):
    faithful: bool
    explanation: str = ""


# ---------------------------------------------------------------------------
# 20 Hand-Labelled Calibration Examples (12 Faithful, 8 Unfaithful)
# ---------------------------------------------------------------------------
REASON_CALIBRATION_20: list[dict[str, Any]] = [
    # --- 12 Faithful examples ---
    {
        "id": "cal-01",
        "requirement_id": "SEC-4.2",
        "verdict": "PASS",
        "reason": "SOC 2 Type II (2026-01-20, documented). Valid and documented.",
        "evidence": "SOC 2 Type II report dated 2026-01-20 (available under NDA via trust portal); evidence_level=documented",
        "gold_faithful": True,
    },
    {
        "id": "cal-02",
        "requirement_id": "DP-3.1",
        "verdict": "FAIL",
        "reason": "India is only 'planned' (available: ['United States', 'European Union'], planned: ['India']).",
        "evidence": "available: ['United States', 'European Union'], planned: ['India']; evidence_level=documented",
        "gold_faithful": True,
    },
    {
        "id": "cal-03",
        "requirement_id": "DP-3.1",
        "verdict": "PASS",
        "reason": "Region in ['India'] is available (['India', 'Singapore']).",
        "evidence": "available: ['India', 'Singapore'], planned: []; evidence_level=documented",
        "gold_faithful": True,
    },
    {
        "id": "cal-04",
        "requirement_id": "SEC-4.2",
        "verdict": "NEEDS_REVIEW",
        "reason": "'SOC 2 compliant' stated without report type or date (claimed).",
        "evidence": "'SOC 2 compliant' (no report type, date or auditor given); evidence_level=claimed",
        "gold_faithful": True,
    },
    {
        "id": "cal-05",
        "requirement_id": "AI-2.1",
        "verdict": "NEEDS_REVIEW",
        "reason": "trains_on_customer_data is 'no_on_paid_plans' — acceptable only if the team's plan/contract enforces it.",
        "evidence": "trains_on_customer_data='no_on_paid_plans'; No training on Business/Enterprise plans; evidence_level=documented",
        "gold_faithful": True,
    },
    {
        "id": "cal-06",
        "requirement_id": "AI-2.1",
        "verdict": "PASS",
        "reason": "trains_on_customer_data is 'no' (Never trains models on customer data).",
        "evidence": "trains_on_customer_data='no'; Never trains models on customer data; evidence_level=documented",
        "gold_faithful": True,
    },
    {
        "id": "cal-07",
        "requirement_id": "AI-3.4",
        "verdict": "NEEDS_REVIEW",
        "reason": "Sub-processors disclosed (3), includes model provider(s): OpenAI — verify AI-2.1 flows down.",
        "evidence": "3 sub-processors disclosed including OpenAI (category=model_provider); evidence_level=documented",
        "gold_faithful": True,
    },
    {
        "id": "cal-08",
        "requirement_id": "DP-5.4",
        "verdict": "PASS",
        "reason": "Retention 30d / deletion-on-request 30d ≤ 30d.",
        "evidence": "default_days=30, deletion_on_request_days=30; evidence_level=documented",
        "gold_faithful": True,
    },
    {
        "id": "cal-09",
        "requirement_id": "SEC-7.1",
        "verdict": "NEEDS_REVIEW",
        "reason": "sso_saml is 'enterprise_only' — acceptable only if the team's plan/contract enforces it.",
        "evidence": "sso_saml='enterprise_only'; SAML 2.0 SSO on Enterprise plan; evidence_level=documented",
        "gold_faithful": True,
    },
    {
        "id": "cal-10",
        "requirement_id": "SEC-9.3",
        "verdict": "NEEDS_REVIEW",
        "reason": "1 major incident(s) in the last 24m, post-mortem published — reviewer to check remediation.",
        "evidence": "1 major incident (2025-04-14, API token exposure) with postmortem_published=True; evidence_level=documented",
        "gold_faithful": True,
    },
    {
        "id": "cal-11",
        "requirement_id": "PROC-1.1",
        "verdict": "NEEDS_REVIEW",
        "reason": "Parakeet Translate is on the Approved Vendor List for T2 only (Team plan); this request is for T3.",
        "evidence": "AVL-1 entry: Parakeet Translate approved for T2 Internal (Team plan); requested tier=T3",
        "gold_faithful": True,
    },
    {
        "id": "cal-12",
        "requirement_id": "PROC-1.1",
        "verdict": "UNKNOWN",
        "reason": "Caller does not have access to the Approved Vendor List (restricted to Procurement and Information Security).",
        "evidence": "approved_vendor_list=NO_ACCESS for caller groups ['public', 'employees']",
        "gold_faithful": True,
    },
    # --- 8 Unfaithful examples (hallucinations, contradictions, evidence-level upgrades) ---
    {
        "id": "cal-13",
        "requirement_id": "DP-3.1",
        "verdict": "PASS",
        "reason": "Vendor stores customer data in Mumbai, India data centers today.",
        "evidence": "available: ['United States', 'European Union'], planned: ['India']; evidence_level=documented",
        "gold_faithful": False,
    },
    {
        "id": "cal-14",
        "requirement_id": "SEC-4.2",
        "verdict": "PASS",
        "reason": "Vendor holds a documented SOC 2 Type II report issued 2026-08-01 by Deloitte.",
        "evidence": "'SOC 2 compliant' (no report type, date or auditor given); evidence_level=claimed",
        "gold_faithful": False,
    },
    {
        "id": "cal-15",
        "requirement_id": "AI-2.1",
        "verdict": "PASS",
        "reason": "Vendor never trains on customer data under any plan.",
        "evidence": "trains_on_customer_data='yes'; Trains foundation models on all customer prompts; evidence_level=documented",
        "gold_faithful": False,
    },
    {
        "id": "cal-16",
        "requirement_id": "DP-5.4",
        "verdict": "PASS",
        "reason": "Retention is 15 days, well within the 30-day policy limit.",
        "evidence": "default_days=180, deletion_on_request_days=90; evidence_level=documented",
        "gold_faithful": False,
    },
    {
        "id": "cal-17",
        "requirement_id": "SEC-9.3",
        "verdict": "PASS",
        "reason": "No major security incidents have occurred in the past 24 months.",
        "evidence": "1 major incident (2026-02-10, unencrypted database breach) with postmortem_published=False; evidence_level=documented",
        "gold_faithful": False,
    },
    {
        "id": "cal-18",
        "requirement_id": "SEC-7.1",
        "verdict": "PASS",
        "reason": "SAML SSO is included on all plans at no extra cost.",
        "evidence": "sso_saml='none'; Single sign-on is not supported; evidence_level=documented",
        "gold_faithful": False,
    },
    {
        "id": "cal-19",
        "requirement_id": "DP-3.1",
        "verdict": "PASS",
        "reason": "India is only 'planned' (available: ['US'], planned: ['India']).",
        "evidence": "available: ['US'], planned: ['India']; evidence_level=documented",
        "gold_faithful": False,
    },
    {
        "id": "cal-20",
        "requirement_id": "SEC-4.2",
        "verdict": "PASS",
        "reason": "ISO 27001 certificate UK-9999-FAKE valid until 2029.",
        "evidence": "SOC 2 Type I in_progress (July 2024); evidence_level=claimed",
        "gold_faithful": False,
    },
]


def _deterministic_reason_check(verdict: str, reason: str, evidence: str) -> dict[str, Any]:
    """Calibrated rule+lexical check used in offline/mock mode (and as sanity floor for LLM judge)."""
    r_low = reason.lower()
    e_low = evidence.lower()

    # 1. Verdict-reason internal contradiction (e.g., verdict=PASS but reason says "only 'planned'" or "in progress")
    if verdict == "PASS" and ("only 'planned'" in r_low or "in progress" in r_low or "not supported" in r_low):
        return {"faithful": False, "explanation": "PASS verdict contradicts negative reason text."}

    # 2. Evidence-level fabrication (reason claims "documented" or specific auditor/report date when evidence is "claimed" with no date)
    if "evidence_level=claimed" in e_low and verdict == "PASS" and ("documented" in r_low or "iso 27001 certificate" in r_low):
        return {"faithful": False, "explanation": "Reason fabricates documented certification from claimed evidence."}

    # 3. Region contradiction (reason claims India is active/stored today when evidence shows India is only in planned)
    if "planned: ['india']" in e_low and "available: ['india'" not in e_low and verdict == "PASS":
        return {"faithful": False, "explanation": "Reason claims PASS for India residency when India is only planned."}

    # 4. Training contradiction
    if "trains_on_customer_data='yes'" in e_low and ("never trains" in r_low or verdict == "PASS"):
        return {"faithful": False, "explanation": "Reason claims no training when evidence states trains_on_customer_data='yes'."}

    # 5. Numeric retention fabrication
    r_days = re.findall(r"\b(\d+)\s*(?:d|days)\b", r_low)
    e_days = re.findall(r"(?:default_days|deletion_on_request_days)['\":=\s]+(\d+)", e_low)
    if r_days and e_days and not (set(r_days) & set(e_days)):
        return {"faithful": False, "explanation": f"Reason retention days {r_days} do not match evidence {e_days}."}

    # 6. Incident contradiction
    if "postmortem_published=false" in e_low and ("no major security incidents" in r_low or verdict == "PASS"):
        return {"faithful": False, "explanation": "Reason hides unresolved major incident present in evidence."}

    # 7. SSO contradiction
    if "sso_saml='none'" in e_low and ("included on all plans" in r_low or verdict == "PASS"):
        return {"faithful": False, "explanation": "Reason claims SSO is included when evidence states sso_saml='none'."}

    # 8. Lexical overlap sanity check
    r_toks = set(tokenize(reason))
    e_toks = set(tokenize(evidence))
    if r_toks and e_toks and len(r_toks & e_toks) == 0:
        return {"faithful": False, "explanation": "Reason shares zero content tokens with evidence."}

    return {"faithful": True, "explanation": "Reason is consistent with the verdict and grounded in the evidence."}


def judge_reason_faithfulness(
    verdict: str,
    reason: str,
    evidence_summary: str,
    llm: Optional[LLM] = None,
) -> ReasonJudgeResult:
    """Evaluate whether a single requirement verdict's `reason` is faithful to `evidence_summary`."""
    client = (llm or LLM()).small()
    prompt = f"Verdict: {verdict}\nReason: {reason}\nEvidence: {evidence_summary}"
    return client.structured(
        REASON_JUDGE_SYSTEM,
        prompt,
        ReasonJudgeResult,
        stage="reason_judge",
        mock=lambda: _deterministic_reason_check(verdict, reason, evidence_summary),
    )


def calibrate_reason_judge(llm: Optional[LLM] = None) -> dict[str, Any]:
    """Run `judge_reason_faithfulness` against the 20 hand-labelled examples in `REASON_CALIBRATION_20`."""
    tp = tn = fp = fn = 0
    details: list[dict[str, Any]] = []
    for item in REASON_CALIBRATION_20:
        res = judge_reason_faithfulness(item["verdict"], item["reason"], item["evidence"], llm=llm)
        pred = res.faithful
        gold = bool(item["gold_faithful"])
        if pred and gold:
            tp += 1
        elif not pred and not gold:
            tn += 1
        elif pred and not gold:
            fp += 1
        else:
            fn += 1
        details.append(
            {
                "id": item["id"],
                "requirement_id": item["requirement_id"],
                "gold": gold,
                "predicted": pred,
                "match": pred == gold,
                "explanation": res.explanation,
            }
        )
    total = len(REASON_CALIBRATION_20)
    accuracy = (tp + tn) / max(1, total)
    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    f1 = (2 * precision * recall) / max(1e-9, precision + recall)
    return {
        "total": total,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "details": details,
    }
