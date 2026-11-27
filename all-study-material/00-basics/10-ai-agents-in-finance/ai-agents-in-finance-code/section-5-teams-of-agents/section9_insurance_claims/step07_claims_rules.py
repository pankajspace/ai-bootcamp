"""
Section 9 lab — the RULES behind the claims pipeline (pure Python: no LLM, no API key)
=====================================================================================
Everything that moves money or blocks a decision lives here, as plain functions:
  fraud score · payout · decision · human-review gates · compliance checks · audit log.
Rules are auditable, repeatable and unit-testable — exactly what a regulator asks for.
The agents in step09_claims_pipeline.py call these functions through their tools.

How to run (free):
    python step07_claims_rules.py                 # Sarah Chen's claim, no LLM at all
    python step07_claims_rules.py --suspicious    # a claim that trips the fraud rules
    python -m pytest step08_test_claims_rules.py -q
"""

from __future__ import annotations

import re
import sys
import uuid
from datetime import date, datetime, timezone
from enum import Enum

from pydantic import BaseModel


class ClaimType(str, Enum):
    AUTO = "auto"
    PROPERTY = "property"
    HEALTH = "health"
    LIABILITY = "liability"


class ClaimRecord(BaseModel):
    """The contract every agent reads and writes. Each stage owns its own fields."""
    claim_id: str
    policyholder_name: str
    policy_number: str
    claim_type: ClaimType
    date_of_loss: date
    description: str
    status: str = "received"
    # DocumentParser
    parsed_documents: list[dict] = []
    damage_description: str = ""
    missing_documents: list[str] = []
    # CoverageAgent
    coverage_verified: bool | None = None
    coverage_section: str = ""
    applicable_limit: float = 0.0
    deductible: float = 0.0
    coverage_reasoning: str = ""
    # FraudScreener
    fraud_score: int | None = None
    red_flags: list[str] = []
    fraud_recommendation: str = ""
    # AssessmentAgent
    estimated_payout: float | None = None
    assessment_breakdown: str = ""
    # DecisionAgent
    decision: str = ""
    decision_reasoning: str = ""
    human_review_gates: list[str] = []
    # ComplianceAgent
    compliance_issues: list[str] = []
    stages_completed: list[str] = []

# Least privilege: which top-level inputs each agent may SEE …
DATA_ACCESS = {
    "FNOLAgent":       ["claim_form"],
    "DocumentParser":  ["submitted_documents"],
    "CoverageAgent":   ["policy"],
    "FraudScreener":   ["policy", "claims_history", "fnol_date"],
    "AssessmentAgent": ["claim_form"],           # the body-shop estimate lines
    "DecisionAgent":   [],                        # works only from the claim record
    "ComplianceAgent": [],
}
# … and which claim fields each agent may WRITE (no agent can overwrite another's work).
OWNED_FIELDS = {
    "DocumentParser":  {"parsed_documents", "damage_description", "missing_documents"},
    "CoverageAgent":   {"coverage_verified", "coverage_section", "applicable_limit",
                        "deductible", "coverage_reasoning"},
    "FraudScreener":   {"fraud_score", "red_flags", "fraud_recommendation"},
    "AssessmentAgent": {"estimated_payout", "assessment_breakdown"},
    "DecisionAgent":   {"decision", "decision_reasoning", "human_review_gates"},
    "ComplianceAgent": {"compliance_issues"},
}


def scoped_view(state: dict, agent: str) -> dict:
    """Give an agent only the inputs it is allowed to see."""
    return {k: state[k] for k in DATA_ACCESS[agent] if k in state}


def write_fields(claim: dict, agent: str, status: str, **fields) -> None:
    """Write an agent's results into the claim — refuse anything it doesn't own."""
    illegal = set(fields) - OWNED_FIELDS[agent]
    if illegal:
        raise PermissionError(f"{agent} may not write {sorted(illegal)}")
    claim.update(fields)
    claim["status"] = status
    claim["stages_completed"] = claim.get("stages_completed", []) + [agent]

def redact(text: str, claim: dict) -> str:
    """Replace the policyholder's name and policy number with opaque tokens."""
    for secret, label in ((claim.get("policyholder_name"), "NAME"),
                          (claim.get("policy_number"), "POLICY")):
        if secret:
            text = re.sub(re.escape(secret), f"[{label}:{claim['claim_id']}]", text, flags=re.I)
    return text


def log_audit(state: dict, agent: str, action: str, details: str = "") -> None:
    """Append-only audit trail. Every agent writes here; nobody edits old lines."""
    claim = state.get("claim", {})
    state.setdefault("audit_log", []).append({
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claim_id": claim.get("claim_id", "?"),
        "agent": agent,
        "action": action,
        "details": redact(details, claim) if claim else details,
    })

AUTO_WORDS = r"\b(car|vehicle|truck|collision|rear-end|bumper|headlight)\b"
PROPERTY_WORDS = r"\b(roof|house|kitchen|fire|flood|burst pipe)\b"


def classify_claim_type(description: str) -> ClaimType:
    d = description.lower()
    if re.search(AUTO_WORDS, d):                    # whole words only: "car" ≠ "careful"
        return ClaimType.AUTO
    if re.search(PROPERTY_WORDS, d):
        return ClaimType.PROPERTY
    return ClaimType.LIABILITY


def fnol_intake(claim_form: dict) -> dict:
    claim = ClaimRecord(
        claim_id=f"CLM-{claim_form['date_of_loss'][:4]}-{uuid.uuid4().hex[:8].upper()}",
        policyholder_name=claim_form["name"],
        policy_number=claim_form["policy_number"],
        claim_type=classify_claim_type(claim_form["description"]),
        date_of_loss=claim_form["date_of_loss"],
        description=claim_form["description"],
    )
    return claim.model_dump(mode="json")


REQUIRED_DOCS = {"claim_form", "photo", "police_report"}


def parse_documents(documents: list[dict]) -> dict:
    parsed = []
    for doc in documents:
        if doc["type"] == "photo":
            # PRODUCTION: send the image to a vision model here.
            # LAB: the photo arrives as a written description standing in for that output.
            parsed.append({"type": "damage_photo", "description": doc["description"]})
        elif doc["type"] in ("claim_form", "police_report"):
            parsed.append(doc)
    seen = {d["type"] for d in documents}
    damage = "; ".join(d["description"] for d in parsed if d["type"] == "damage_photo")
    return {"parsed_documents": parsed, "damage_description": damage,
            "missing_documents": sorted(REQUIRED_DOCS - seen)}

def days_between(a, b) -> int:
    to_d = lambda x: x if isinstance(x, date) else date.fromisoformat(x)
    return (to_d(b) - to_d(a)).days


def verify_coverage(claim: dict, policy: dict) -> dict:
    # PRODUCTION: an LLM reads the policy wording and cites sections. LAB: keyword rules.
    loss, desc = claim["date_of_loss"], claim["description"].lower()
    started = days_between(policy["inception_date"], loss) >= 0     # loss on/after the start
    not_ended = days_between(loss, policy["expiry_date"]) >= 0      # loss on/before the end
    if not (started and not_ended):
        return {"coverage_verified": False, "coverage_section": "",
                "applicable_limit": 0.0, "deductible": 0.0,
                "coverage_reasoning": "POLICY_INACTIVE: loss date outside the policy period."}
    for ex in policy["exclusions"]:
        if any(k in desc for k in ex["keywords"]):
            return {"coverage_verified": False, "coverage_section": ex["ref"],
                    "applicable_limit": 0.0, "deductible": 0.0,
                    "coverage_reasoning": f"EXCLUSION: {ex['ref']} applies ({ex['label']})."}
    for sec in policy["coverage_sections"]:
        if any(k in desc for k in sec["keywords"]):
            return {"coverage_verified": True, "coverage_section": sec["ref"],
                    "applicable_limit": float(sec["limit"]), "deductible": float(sec["deductible"]),
                    "coverage_reasoning": (f"Covered under {sec['ref']}: limit ${sec['limit']:,}, "
                                           f"deductible ${sec['deductible']:,}.")}
    return {"coverage_verified": None, "coverage_section": "", "applicable_limit": 0.0,
            "deductible": 0.0, "coverage_reasoning": "AMBIGUOUS: no section clearly applies."}

FRAUD_THRESHOLD = 40


def screen_for_fraud(policy: dict, claim: dict, claims_history: list, fnol_date: str) -> dict:
    score, flags = 0, []
    if days_between(policy["inception_date"], claim["date_of_loss"]) < 30:
        score += 25
        flags.append("Loss within 30 days of policy start (buy-and-claim pattern)")
    if len(claims_history) >= 3:
        score += 20
        flags.append(f"{len(claims_history)} prior claims in 12 months")
    if days_between(claim["date_of_loss"], fnol_date) > 30:
        score += 15
        flags.append("Reported more than 30 days after the loss")
    return {"fraud_score": score, "red_flags": flags,
            "fraud_recommendation": "investigate" if score > FRAUD_THRESHOLD else "proceed"}

def assess_damage(repair_items: list[dict], deductible: float, limit: float) -> dict:
    # PRODUCTION: a vision/LLM estimate from photos, checked against a body-shop quote.
    gross = sum(i["cost"] for i in repair_items)
    payout = max(0.0, min(gross - deductible, limit))     # never negative, never above limit
    lines = ", ".join(f"{i['item']} ${i['cost']:,}" for i in repair_items)
    return {"estimated_payout": payout,
            "assessment_breakdown": f"{lines} = ${gross:,} gross − ${deductible:,.0f} deductible"
                                    f" → ${payout:,.0f} (limit ${limit:,.0f})"}

HIGH_VALUE_THRESHOLD = 100_000


def human_review_gates(claim: dict) -> list[str]:
    gates = []
    if (claim.get("estimated_payout") or 0) > HIGH_VALUE_THRESHOLD:
        gates.append("HIGH_VALUE → senior adjuster")
    if (claim.get("fraud_score") or 0) > FRAUD_THRESHOLD:
        gates.append("FRAUD_FLAG → fraud investigation / SIU")
    if claim.get("coverage_verified") is None:
        gates.append("COVERAGE_AMBIGUOUS → coverage specialist")
    if claim.get("claim_type") in ("health", "liability"):
        gates.append("REGULATORY → bodily-injury adjuster")
    if claim.get("missing_documents"):
        gates.append("INCOMPLETE_DOCS → request " + ", ".join(claim["missing_documents"]))
    return gates


STATUS_AFTER = {"APPROVE": "approved", "DENY": "denied", "ESCALATE": "escalated"}


def make_decision(claim: dict) -> dict:
    # PRODUCTION: an LLM writes the reasoning; the CHOICE still follows these rules.
    gates = human_review_gates(claim)
    if claim["coverage_verified"] is False:
        decision = "DENY"
        reasoning = (f"{claim['coverage_reasoning']} Policy reference: "
                     f"{claim['coverage_section'] or 'policy period'}. The claimant may contact "
                     "the state Department of Insurance.")
    elif gates:
        decision = "ESCALATE"
        reasoning = ("Paused for human review: " + "; ".join(gates) +
                     f". Fraud score {claim['fraud_score']}/100; proposed payout "
                     f"${claim['estimated_payout']:,.0f}.")
    else:
        decision = "APPROVE"
        reasoning = (f"{claim['coverage_reasoning']} Fraud score {claim['fraud_score']}/100 "
                     f"with no red flags. Payout: {claim['assessment_breakdown']}.")
    return {"decision": decision, "decision_reasoning": reasoning, "human_review_gates": gates}

DENIAL_REASONS = ("POLICY_INACTIVE", "EXCLUSION", "NOT_COVERED")
ALL_STAGES = ["DocumentParser", "CoverageAgent", "FraudScreener", "AssessmentAgent", "DecisionAgent"]


def validate_compliance(claim: dict) -> list[str]:
    issues = []
    if claim["decision"] == "DENY" and not claim["decision_reasoning"].startswith(DENIAL_REASONS):
        issues.append("Denial reason not a recognised category")
    if len(claim["decision_reasoning"]) < 50:
        issues.append("Reasoning too short for an audit")
    missing = [s for s in ALL_STAGES if s not in claim.get("stages_completed", [])]
    if missing:
        issues.append(f"Pipeline stage missing: {missing}")
    if claim["decision"] == "APPROVE":
        if (claim.get("fraud_score") or 0) > FRAUD_THRESHOLD:
            issues.append("Approved despite a fraud flag")
        if (claim.get("estimated_payout") or 0) > claim.get("applicable_limit", 0):
            issues.append("Payout above the policy limit")
        if claim.get("human_review_gates"):
            issues.append("Auto-approved although a human-review gate fired")
    return issues

SAMPLE_POLICY = {
    "policy_number": "FWS-AUTO-58213", "holder": "Sarah Chen",
    "inception_date": "2025-11-02", "expiry_date": "2026-11-01",
    "coverage_sections": [
        {"ref": "Part D §1 Collision", "keywords": ["collision", "rear-end", "hit a"],
         "limit": 50_000, "deductible": 500},
        {"ref": "Part D §2 Comprehensive", "keywords": ["theft", "stolen", "hail", "flood"],
         "limit": 50_000, "deductible": 250},
    ],
    "exclusions": [{"ref": "Exclusion 4", "label": "racing or intentional damage",
                    "keywords": ["racing", "intentional"]}],
}
SAMPLE_CLAIM_FORM = {
    "type": "claim_form", "name": "Sarah Chen", "policy_number": "FWS-AUTO-58213",
    "date_of_loss": "2026-04-07",
    "description": ("Rear-end collision on I-95 at 2:47 AM in rain: my car hit a stopped "
                    "delivery truck. Front bumper and headlight damaged. No injuries at the "
                    "scene; back pain noted later (separate injury feature)."),
    "repair_items": [{"item": "front bumper", "cost": 2_600},
                     {"item": "headlight assembly", "cost": 1_100},
                     {"item": "labour", "cost": 600}],
}
SAMPLE_DOCUMENTS = [
    SAMPLE_CLAIM_FORM,
    {"type": "photo", "description": "Front bumper crushed, grille cracked"},
    {"type": "photo", "description": "Left headlight assembly shattered"},
    {"type": "police_report", "report_number": "HP-2026-0407-118",
     "summary": "Vehicle 1 struck a stationary delivery truck; wet road; no citations."},
]


def sample_state(suspicious: bool = False) -> dict:
    """The starting whiteboard for one claim. suspicious=True trips all three fraud rules."""
    state = {"claim_form": SAMPLE_CLAIM_FORM, "submitted_documents": SAMPLE_DOCUMENTS,
             "policy": SAMPLE_POLICY, "claims_history": [], "fnol_date": "2026-04-08",
             "audit_log": []}
    if suspicious:
        state["policy"] = {**SAMPLE_POLICY, "inception_date": "2026-03-20"}   # 18 days before
        state["claims_history"] = [{"id": "C1"}, {"id": "C2"}, {"id": "C3"}]
        state["fnol_date"] = "2026-05-15"                                      # 38 days late
    return state

def run_offline(state: dict) -> dict:
    """The same seven stages as the agent pipeline, called directly — handy for tests."""
    claim = fnol_intake(state["claim_form"]); state["claim"] = claim
    log_audit(state, "FNOLAgent", "claim created",
              f"{claim['policyholder_name']} / {claim['policy_number']}, type={claim['claim_type']}")
    r = parse_documents(state["submitted_documents"])
    write_fields(claim, "DocumentParser", "parsing", **r)
    log_audit(state, "DocumentParser", "documents parsed", f"{len(r['parsed_documents'])} docs")
    r = verify_coverage(claim, state["policy"])
    write_fields(claim, "CoverageAgent", "coverage_check", **r)
    log_audit(state, "CoverageAgent", "coverage checked", r["coverage_reasoning"])
    r = screen_for_fraud(state["policy"], claim, state["claims_history"], state["fnol_date"])
    write_fields(claim, "FraudScreener", "fraud_screening", **r)
    log_audit(state, "FraudScreener", "fraud screened", f"score={r['fraud_score']} {r['red_flags']}")
    r = assess_damage(state["claim_form"]["repair_items"], claim["deductible"], claim["applicable_limit"])
    write_fields(claim, "AssessmentAgent", "assessment", **r)
    log_audit(state, "AssessmentAgent", "damage assessed", r["assessment_breakdown"])
    r = make_decision(claim)
    write_fields(claim, "DecisionAgent", STATUS_AFTER[r["decision"]], **r)
    log_audit(state, "DecisionAgent", f"decision {r['decision']}", r["decision_reasoning"])
    issues = validate_compliance(claim)
    write_fields(claim, "ComplianceAgent", "blocked" if issues else "compliance_ok", compliance_issues=issues)
    log_audit(state, "ComplianceAgent", "BLOCKED" if issues else "validated", str(issues or "compliant"))
    return state


if __name__ == "__main__":
    final = run_offline(sample_state(suspicious="--suspicious" in sys.argv))
    c = final["claim"]
    print(f"{c['claim_id']}: {c['decision']}  payout ${c['estimated_payout']:,.0f}  "
          f"fraud {c['fraud_score']}/100  compliance issues: {c['compliance_issues'] or 'none'}")
    print("\nAudit log (PII redacted):")
    for row in final["audit_log"]:
        print(f"  {row['agent']:16} {row['action']:18} {row['details']}")
