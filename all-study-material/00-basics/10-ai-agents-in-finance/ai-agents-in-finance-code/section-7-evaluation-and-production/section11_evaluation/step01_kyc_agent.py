"""
Section 11 lab — the system under test: a stand-in KYC onboarding pipeline
==========================================================================
The real pipeline is seven LLM agents in a row:

  intake → document_verification → sanctions_screening → adverse_media
         → risk_scoring → decision → compliance_guardrail

To learn EVALUATION we need something that behaves like that pipeline, runs in
milliseconds for free, and can be broken on purpose. This file is that stand-in:
the bank's written risk rules, a little "LLM-like" noise near the tier
boundaries, and FAULT switches that reproduce real production failures.

How to run
----------
No installs, no API key (Python 3.10+):
    python step01_kyc_agent.py                  # one clean case
    python step01_kyc_agent.py log_raw_pii      # the same case with a fault switched on

In production you'd replace run_pipeline() with a call to your real agents.
The evaluation harness (step03_kyc_eval.py) doesn't care which one it is testing.
"""

from __future__ import annotations

import random
import sys
from dataclasses import dataclass, field

PIPELINE = ["intake", "document_verification", "sanctions_screening", "adverse_media",
            "risk_scoring", "decision", "compliance_guardrail"]   # required, in this order
HIGH_RISK_JURISDICTIONS = {"XR", "YR"}          # fictional country codes
CASH_INTENSIVE = {"money services", "car dealer", "casino supplier"}
TIERS = ["LOW", "MEDIUM", "HIGH", "PROHIBITED"]


@dataclass
class Applicant:
    case_id: str
    name: str
    country: str
    occupation: str
    pep: bool                     # politically exposed person
    sanctions_hit: bool           # TRUE match on a sanctions list
    adverse_media: int            # credible negative news items found
    doc_confidence: float         # 0–1 from the document check
    group: str                    # demographic segment: used ONLY to test fairness
    free_text: str = ""           # customer-written notes (may hide a prompt injection)
    ssn: str = ""                 # personal data that must never reach the logs


@dataclass
class Decision:
    case_id: str
    risk_tier: str                # LOW / MEDIUM / HIGH / PROHIBITED
    outcome: str                  # APPROVE / EDD (enhanced due diligence) / DECLINE
    trajectory: list[str]         # stages that actually ran, in order
    evidence: dict                # what each stage returned (what claims may cite)
    reasoning: list[dict]         # [{"claim": ..., "source": stage or None}]
    audit_log: str
    latency_s: float
    cost_usd: float


FAULTS = {                        # switch these on to break the pipeline on purpose
    "skip_sanctions_on_timeout": "sanctions API times out on ~30% of cases; the run silently continues",
    "log_raw_pii": "the audit log prints the full SSN instead of the last four digits",
    "follow_injection": "the decision agent obeys instructions hidden in customer notes",
    "biased_rule": "a proxy variable adds risk points to one demographic group",
    "hallucinate_reason": "the decision agent adds a reason that no tool returned",
    "slow_tail": "5% of cases hit a slow model endpoint (70–120 s)",
}

def risk_points(app: Applicant) -> int:
    """The bank's written risk-tier rules. This is what a human expert would apply."""
    points = 0
    points += 40 if app.pep else 0
    points += 15 * min(app.adverse_media, 3)
    points += 25 if app.doc_confidence < 0.70 else 0
    points += 30 if app.country in HIGH_RISK_JURISDICTIONS else 0
    points += 10 if app.occupation in CASH_INTENSIVE else 0
    return points


def tier_from_points(points: int, sanctions_hit: bool) -> str:
    if sanctions_hit:
        return "PROHIBITED"
    return "HIGH" if points >= 70 else "MEDIUM" if points >= 35 else "LOW"


def reference_tier(app: Applicant) -> str:
    """Ground truth for the evaluation set: the rules, applied perfectly."""
    return tier_from_points(risk_points(app), app.sanctions_hit)


def outcome_for(tier: str) -> str:
    return {"LOW": "APPROVE", "MEDIUM": "APPROVE", "HIGH": "EDD", "PROHIBITED": "DECLINE"}[tier]

INJECTION_MARKERS = ("ignore previous", "ignore all previous", "system:", "set risk tier", "approve this")


def run_pipeline(app: Applicant, faults: set[str] | None = None, seed: int = 0) -> Decision:
    """Run the seven stages for one applicant and return the decision + its paper trail."""
    faults = faults or set()
    rng = random.Random(f"{app.case_id}-{seed}")       # same case + seed → same run
    frng = random.Random(f"{app.case_id}-{seed}-fault")   # faults get their own dice
    trajectory, evidence = [], {}

    trajectory.append("intake")
    evidence["intake"] = {"pep": app.pep, "country": app.country, "occupation": app.occupation}

    trajectory.append("document_verification")
    evidence["document_verification"] = {"doc_confidence": app.doc_confidence}

    if "skip_sanctions_on_timeout" in faults and frng.random() < 0.30:
        evidence["sanctions_screening"] = None          # timed out → silently skipped
    else:
        trajectory.append("sanctions_screening")
        evidence["sanctions_screening"] = {"match": app.sanctions_hit}
    sanctions_seen = bool(evidence["sanctions_screening"] and evidence["sanctions_screening"]["match"])

    trajectory.append("adverse_media")
    evidence["adverse_media"] = {"items": app.adverse_media}

    trajectory.append("risk_scoring")
    points = risk_points(app)
    if "biased_rule" in faults and app.group == "B":
        points += 20                                     # proxy discrimination
    evidence["risk_scoring"] = {"points": points}

    trajectory.append("decision")
    tier = tier_from_points(points, sanctions_seen)
    for edge, below, above in ((35, "LOW", "MEDIUM"), (70, "MEDIUM", "HIGH")):
        if tier in (below, above) and abs(points - edge) <= 5 and rng.random() < 0.10:
            tier = above if tier == below else below     # LLM-like wobble near a boundary
    injected = any(m in app.free_text.lower() for m in INJECTION_MARKERS)
    if "follow_injection" in faults and injected and tier != "PROHIBITED":
        tier = "LOW"                                     # obeyed the customer's "instruction"

    reasoning = [
        {"claim": f"Sanctions screening: {'match' if sanctions_seen else 'no match'}.",
         "source": "sanctions_screening" if evidence["sanctions_screening"] is not None else None},
        {"claim": f"PEP status: {'yes' if app.pep else 'no'}.", "source": "intake"},
        {"claim": f"Adverse media items: {app.adverse_media}.", "source": "adverse_media"},
        {"claim": f"Risk points {points} → tier {tier}.", "source": "risk_scoring"},
    ]
    if "hallucinate_reason" in faults and frng.random() < 0.5:
        reasoning.append({"claim": "Customer has a ten-year relationship with the bank.", "source": None})

    trajectory.append("compliance_guardrail")
    ssn_shown = app.ssn if "log_raw_pii" in faults else f"***-**-{app.ssn[-4:]}"
    audit = f"case={app.case_id} ssn={ssn_shown} tier={tier} stages={len(trajectory)}"

    latency = rng.uniform(8, 25) + (frng.uniform(70, 120) if "slow_tail" in faults and frng.random() < 0.05 else 0)
    cost = round(0.12 + 0.03 * len(trajectory) + rng.uniform(0, 0.08), 3)
    return Decision(app.case_id, tier, outcome_for(tier), trajectory, evidence, reasoning, audit,
                    round(latency, 1), cost)

if __name__ == "__main__":
    demo = Applicant("C-0001", "Mara Velin", "GB", "teacher", pep=True, sanctions_hit=False,
                     adverse_media=1, doc_confidence=0.92, group="A", ssn="900-12-3456")
    chosen = set(sys.argv[1:])
    unknown = chosen - set(FAULTS)
    if unknown:
        sys.exit(f"Unknown fault(s) {sorted(unknown)}. Choose from: {', '.join(FAULTS)}")
    d = run_pipeline(demo, chosen)
    print(f"tier={d.risk_tier} outcome={d.outcome} (reference: {reference_tier(demo)})")
    print("trajectory:", " → ".join(d.trajectory))
    for r in d.reasoning:
        print(f"  - {r['claim']:<45} source={r['source']}")
    print("audit log:", d.audit_log)
    print(f"latency {d.latency_s}s · cost ${d.cost_usd}")
