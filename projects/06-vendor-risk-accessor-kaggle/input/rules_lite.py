"""
rules_lite.py — the competition's verdict rules, with no dependencies beyond the standard library.

This is the deterministic matcher from the AI Vendor Risk Assessor capstone, rewritten to work on plain
dicts. The gold labels were produced by the original matcher; a test in the host repo checks that
this file gives identical answers.

YOUR JOB is to read the pages and build the `facts` dict. These rules turn facts into verdicts.

facts = {
  "security_certifications": {"value": [ {"name": "SOC 2 Type II", "status": "certified", "date": "2026-01-20", "valid_until": None}, ... ],
                              "evidence_level": "documented" | "claimed"},
  "data_regions":            {"value": {"available": ["United States"], "planned": ["India"]}},
  "trains_on_customer_data": {"value": "no" | "no_on_paid_plans" | "opt_out_available" | "yes"},
  "subprocessors":           {"value": [ {"name": "...", "category": "model_provider", "country": "..."} , ... ]},
  "data_retention":          {"value": {"default_days": 30, "deletion_on_request_days": None}},
  "sso_saml":                {"value": "all_plans" | "paid_plans" | "enterprise_only" | "none"},
  "security_incidents":      {"value": [ {"date": "2026-03-02", "summary": "...", "severity": "major", "postmortem_published": False} ]},
  "dpa_available":           {"value": "yes" | "on_request" | "no"},
}
A field that official sources do not state is simply MISSING from `facts` (or its value is None) -> UNKNOWN.
Cert names: "SOC 2 Type II", "SOC 2 Type I", "SOC 2" (type not stated), "ISO 27001", or any other name.
Cert status: "certified" | "in_progress".   Severity: "major" | "critical" | "minor".
Subprocessor categories: hosting | email | analytics | support | model_provider.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

VERDICTS = ("PASS", "FAIL", "UNKNOWN", "NEEDS_REVIEW")
OVERALL = ("BLOCKED", "CONDITIONAL", "READY_FOR_APPROVAL")


def load_requirements(path: str | Path = "requirements.json") -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _norm(s) -> str:
    return " ".join(str(s).lower().replace("/", " ").replace("-", " ").split())


def _months_between(a: date, b: date) -> float:
    return abs((a - b).days) / 30.44


def applies(req: dict, tier: str, users: int) -> bool:
    aw = req["applies_when"]
    if tier in aw["tiers"]:
        return True
    return aw.get("or_min_users") is not None and users >= aw["or_min_users"]


def _certification_valid(req, fact, as_of):
    if fact is None or not fact.get("value"):
        return "UNKNOWN"
    p = req["params"]
    accepted = {_norm(a) for a in p.get("accepted", [])}
    max_age = int(p.get("max_age_months", 15))
    require_documented = bool(p.get("require_documented", True))
    certs = list(fact["value"])
    matches = [c for c in certs if _norm(c.get("name", "")) in accepted]
    generic_soc2 = [c for c in certs if _norm(c.get("name", "")) == "soc 2" and c.get("status") == "certified"]
    certified = [c for c in matches if c.get("status") == "certified"]

    def is_current(c):
        if c.get("valid_until"):
            return date.fromisoformat(str(c["valid_until"])) >= as_of
        d = c.get("date")
        return bool(d) and _months_between(as_of, date.fromisoformat(str(d))) <= max_age

    if [c for c in certified if is_current(c)]:
        if require_documented and fact.get("evidence_level") != "documented":
            return "NEEDS_REVIEW"
        return "PASS"
    if certified:
        return "NEEDS_REVIEW"
    if generic_soc2:
        return "NEEDS_REVIEW"
    return "FAIL"


def _region_includes(req, fact, as_of):
    if fact is None or not isinstance(fact.get("value"), dict):
        return "UNKNOWN"
    wanted = {_norm(x) for x in req["params"].get("any_of", [])}
    available = {_norm(x) for x in fact["value"].get("available", [])}
    planned = {_norm(x) for x in fact["value"].get("planned", [])}
    if wanted & available:
        return "PASS"
    if wanted & planned and not req["params"].get("allow_planned", False):
        return "FAIL"
    if available:
        return "FAIL"
    return "UNKNOWN"


def _value_known(req, fact, as_of):
    if fact is None:
        return "UNKNOWN"
    v = fact.get("value")
    if isinstance(v, dict) and not v.get("available"):
        return "UNKNOWN"
    return "PASS"


def _enum_verdict(req, fact, as_of):
    if fact is None or fact.get("value") in (None, ""):
        return "UNKNOWN"
    v, p = str(fact["value"]), req["params"]
    if v in p.get("pass", []):
        return "PASS"
    if v in p.get("review", []):
        return "NEEDS_REVIEW"
    if v in p.get("fail", []):
        return "FAIL"
    return "UNKNOWN"


def _list_disclosed(req, fact, as_of):
    if fact is None or not fact.get("value"):
        return "UNKNOWN"
    flag = set(req["params"].get("review_if_category", []))
    return "NEEDS_REVIEW" if any(i.get("category") in flag for i in fact["value"]) else "PASS"


def _retention_within(req, fact, as_of):
    if fact is None or not isinstance(fact.get("value"), dict):
        return "UNKNOWN"
    max_days = int(req["params"].get("max_days", 30))
    default_days = fact["value"].get("default_days")
    on_request = fact["value"].get("deletion_on_request_days")
    if default_days is not None and int(default_days) <= max_days:
        return "PASS"
    if default_days is None and on_request is not None and int(on_request) <= max_days:
        return "NEEDS_REVIEW"
    if default_days is not None and on_request is not None and int(on_request) <= max_days:
        return "NEEDS_REVIEW"
    if default_days is not None and on_request is None:
        return "NEEDS_REVIEW"
    return "FAIL"


def _no_unresolved_incident(req, fact, as_of):
    if fact is None or fact.get("value") is None:
        return "UNKNOWN"
    lookback = as_of - timedelta(days=int(req["params"].get("lookback_months", 24)) * 30)
    majors = {s.lower() for s in req["params"].get("major_severities", ["major", "critical"])}
    recent = [i for i in fact["value"] if i.get("date") and date.fromisoformat(str(i["date"])) >= lookback]
    major = [i for i in recent if str(i.get("severity", "")).lower() in majors]
    if [i for i in major if not i.get("postmortem_published")]:
        return "FAIL"
    return "NEEDS_REVIEW" if major else "PASS"


RULES = {
    "certification_valid": _certification_valid,
    "region_includes": _region_includes,
    "value_known": _value_known,
    "enum_verdict": _enum_verdict,
    "list_disclosed": _list_disclosed,
    "retention_within": _retention_within,
    "no_unresolved_incident": _no_unresolved_incident,
}


def evaluate(facts: dict, requirements: list[dict], tier: str, users: int, as_of: date | str) -> dict[str, str]:
    """Return {requirement_id: verdict} for every requirement that applies to this tier and user count."""
    as_of = date.fromisoformat(str(as_of))
    out = {}
    for req in requirements:
        if applies(req, tier, users):
            out[req["id"]] = RULES[req["rule"]](req, facts.get(req["field"]), as_of)
    return out


def overall(verdicts: dict[str, str], requirements: list[dict]) -> str:
    """BLOCKED if a blocker FAILs; CONDITIONAL if a major FAILs or anything is UNKNOWN / NEEDS_REVIEW; else READY_FOR_APPROVAL."""
    sev = {r["id"]: r["severity"] for r in requirements}
    if any(v == "FAIL" and sev[k] == "blocker" for k, v in verdicts.items()):
        return "BLOCKED"
    if any(v == "FAIL" and sev[k] == "major" for k, v in verdicts.items()) or any(v in ("UNKNOWN", "NEEDS_REVIEW") for v in verdicts.values()):
        return "CONDITIONAL"
    return "READY_FOR_APPROVAL"
