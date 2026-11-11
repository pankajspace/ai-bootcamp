"""
naive_baseline.py — a deliberately crude starter that writes a valid submission.csv.

It pools the text of EVERY page for a case and looks for keywords. That is exactly the mistake the
competition is built to punish: it trusts forums and look-alike companies, obeys injected text, ignores
dates and cannot tell a claim from a report. Beat it by fixing those things.

    python naive_baseline.py --data . --out submission.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import date, timedelta
from pathlib import Path

import rules_lite as rl


def crude_facts(text: str, as_of: date) -> dict:
    low = text.lower()
    facts: dict = {}
    certs = []
    if "soc 2 type ii" in low:
        certs.append({"name": "SOC 2 Type II", "status": "certified", "date": (as_of - timedelta(days=100)).isoformat()})
    if "iso/iec 27001" in low or "iso 27001" in low:
        certs.append({"name": "ISO 27001", "status": "certified", "valid_until": (as_of + timedelta(days=365)).isoformat()})
    if certs:
        facts["security_certifications"] = {"value": certs, "evidence_level": "documented" if "report" in low else "claimed"}
    regions = [r for r in ("India", "United States", "European Union", "Singapore", "Canada", "Australia", "United Kingdom", "Japan", "Germany") if r.lower() in low]
    if regions:
        facts["data_regions"] = {"value": {"available": regions, "planned": []}}
    if re.search(r"never use|not used for|is switched off|not used for model training", low):
        facts["trains_on_customer_data"] = {"value": "no"}
    elif "opt out" in low or "turns off" in low:
        facts["trains_on_customer_data"] = {"value": "opt_out_available"}
    elif "train" in low:
        facts["trains_on_customer_data"] = {"value": "yes"}
    if "sub-processor" in low or "provides" in low:
        cat = "model_provider" if "language model" in low or "ai model" in low else "hosting"
        facts["subprocessors"] = {"value": [{"name": "?", "category": cat}]}
    m = re.search(r"(\d+) days", low)
    if m:
        facts["data_retention"] = {"value": {"default_days": int(m.group(1)), "deletion_on_request_days": None}}
    if "enterprise plan only" in low or "enterprise feature" in low:
        facts["sso_saml"] = {"value": "enterprise_only"}
    elif "paid" in low and "single sign-on" in low:
        facts["sso_saml"] = {"value": "paid_plans"}
    elif "every plan" in low or "all plans" in low:
        facts["sso_saml"] = {"value": "all_plans"}
    if "no security incident" in low:
        facts["security_incidents"] = {"value": []}
    elif "major" in low or "critical" in low:
        facts["security_incidents"] = {"value": [{"date": (as_of - timedelta(days=100)).isoformat(), "severity": "major", "postmortem_published": "published" in low}]}
    if "on request" in low:
        facts["dpa_available"] = {"value": "on_request"}
    elif "dpa" in low or "data processing agreement" in low:
        facts["dpa_available"] = {"value": "yes"}
    return facts


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=".")
    ap.add_argument("--out", default="submission.csv")
    a = ap.parse_args()
    d = Path(a.data)
    reqs = rl.load_requirements(d / "requirements.json")
    cases = {r["case_id"]: r for r in csv.DictReader((d / "cases.csv").open(encoding="utf-8"))}
    texts: dict[str, list[str]] = {}
    for line in (d / "pages.jsonl").open(encoding="utf-8"):
        p = json.loads(line)
        texts.setdefault(p["case_id"], []).append(p["text"])
    test_rows = list(csv.DictReader((d / "test.csv").open(encoding="utf-8")))
    cache: dict[str, tuple[dict, str]] = {}
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "verdict"])
        for row in test_rows:
            cid = row["case_id"]
            if cid not in cache:
                c = cases[cid]
                as_of = date.fromisoformat(c["as_of"])
                v = rl.evaluate(crude_facts("\n".join(texts[cid]), as_of), reqs, c["tier"], int(c["users"]), as_of)
                cache[cid] = (v, rl.overall(v, reqs))
            v, ov = cache[cid]
            w.writerow([row["id"], ov if row["requirement_id"] == "OVERALL" else v.get(row["requirement_id"], "UNKNOWN")])
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
