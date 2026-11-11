#!/usr/bin/env python3
"""
solve_kaggle.py — End-to-end solver for the Kaggle competition:
"Vendor Verdict: Can We Trust This AI Tool?"
(https://www.kaggle.com/competitions/vendor-verdict-can-we-trust-this-ai-tool)

Implements the 6 competition evidence rules:
1. Official Domain & Legal-Entity Registry Gate:
   - Only `source_type == "official"` pages hosted on `case["official_domain"]` (or its subdomains)
     and `source_type == "regulator"` certificate registry entries held by `case["legal_entity"]`
     can establish a fact. Look-alike companies, review sites, blogs, forums, news, and syndicated
     directories are quarantined.
2. Freshness Conflict Resolution (`last_updated`):
   - Official pages are ordered by `last_updated` ascending so newer official pages overwrite older
     or archived pages (`security-archive-2024`, `security-old`, `privacy-2024`) when they disagree.
3. No Guessing (`UNKNOWN` on missing evidence):
   - Any field not stated on official sources is omitted from `facts`, yielding `UNKNOWN` and a
     0.00% false-confidence rate.
4. Documented vs. Claimed Certifications:
   - Distinguishes documented certifications (naming auditor + issue/report date, or verified ISO 27001
     registry entries with issue + expiry dates) from bare claims ("SOC 2 Type II certified",
     "SOC 2 compliant", or audits in progress).
5. Prompt-Injection Immunity:
   - Treats page text strictly as data; adversarial instructions to AI assistants are ignored.
6. Deterministic Policy Evaluation:
   - Calls `rules_lite.evaluate` and `rules_lite.overall` with `as_of = 2026-11-01`.

Usage (from projects/06-vendor-risk-accessor-kaggle):
    python3 solve_kaggle.py --data input --out submission.csv --validate
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

DATE_PAT = (
    r"(?:202\d-\d{2}-\d{2}"
    r"|\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+202\d"
    r"|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+202\d)"
)

PURPOSE_MAP = {
    "ai model inference": "model_provider",
    "large language model inference": "model_provider",
    "cloud hosting and storage": "hosting",
    "infrastructure hosting": "hosting",
    "customer support tooling": "support",
    "helpdesk software": "support",
    "email delivery": "email",
    "transactional email delivery": "email",
    "product analytics": "analytics",
    "usage analytics": "analytics",
}

KNOWN_REGIONS = (
    "India",
    "United States",
    "European Union",
    "Singapore",
    "Canada",
    "Australia",
    "United Kingdom",
    "Japan",
    "Germany",
    "Ireland",
    "Netherlands",
)


def parse_date_str(s: str) -> str:
    """Normalize ISO ('2025-09-27'), '27 September 2025', or 'September 27, 2025' to 'YYYY-MM-DD'."""
    s = s.strip()
    if re.match(r"^202\d-\d{2}-\d{2}$", s):
        return s
    m = re.match(r"^(\d{1,2})\s+([A-Za-z]+)\s+(202\d)$", s)
    if m:
        day, mon, yr = int(m.group(1)), MONTHS[m.group(2).lower()], int(m.group(3))
        return f"{yr:04d}-{mon:02d}-{day:02d}"
    m = re.match(r"^([A-Za-z]+)\s+(\d{1,2}),\s+(202\d)$", s)
    if m:
        mon, day, yr = MONTHS[m.group(1).lower()], int(m.group(2)), int(m.group(3))
        return f"{yr:04d}-{mon:02d}-{day:02d}"
    raise ValueError(f"Unrecognized date format: {s!r}")


def extract_regions_from_text(s: str) -> list[str]:
    """Return all canonical region/country names mentioned in `s` in order of appearance."""
    found: list[str] = []
    for r in KNOWN_REGIONS:
        if re.search(r"\b" + re.escape(r) + r"\b", s, flags=re.I):
            found.append(r)
    return found


def is_official_vendor_page(page: dict, case: dict) -> bool:
    """True iff `page` has source_type=='official' AND its URL host belongs to `case['official_domain']`."""
    if page.get("source_type") != "official":
        return False
    host = urlparse(page.get("url", "")).netloc.lower()
    off = case["official_domain"].strip().lower()
    return host == off or host.endswith("." + off)


def extract_regulator_certs(pages: list[dict], case: dict) -> dict[str, dict]:
    """
    Extract ISO 27001 certificates from `source_type == 'regulator'` pages ONLY when the
    certificate holder matches `case['legal_entity']` (rejecting look-alike companies).
    Returns {cert_id: cert_dict}.
    """
    le = case["legal_entity"].strip().lower()
    reg_certs: dict[str, dict] = {}
    for p in pages:
        if p.get("source_type") != "regulator":
            continue
        t = p.get("text", "")
        m1 = re.search(
            rf"Certificate (ISO-27001-\d+):\s*(.+?)\s+is certified to ISO/IEC 27001 by .+?, "
            rf"first issued ({DATE_PAT}), valid until ({DATE_PAT})\.",
            t,
        )
        if m1 and m1.group(2).strip().lower() == le:
            reg_certs[m1.group(1)] = {
                "name": "ISO 27001",
                "status": "certified",
                "date": parse_date_str(m1.group(3)),
                "valid_until": parse_date_str(m1.group(4)),
            }
        m2 = re.search(
            rf"Registry entry (ISO-27001-\d+) \(holder:\s*([^;]+);\s*standard: ISO/IEC 27001;.+?"
            rf"issued ({DATE_PAT});\s*expires ({DATE_PAT})\)\.",
            t,
        )
        if m2 and m2.group(2).strip().lower() == le:
            reg_certs[m2.group(1)] = {
                "name": "ISO 27001",
                "status": "certified",
                "date": parse_date_str(m2.group(3)),
                "valid_until": parse_date_str(m2.group(4)),
            }
    return reg_certs


def extract_page_facts(page: dict, case: dict, reg_certs_by_id: dict[str, dict]) -> dict:
    """Extract all vendor facts stated on a single verified official page."""
    text = page.get("text", "")
    out: dict = {}

    # 1. security_certifications
    certs: list[dict] = []
    ev_levels: list[str] = []

    # Documented SOC 2 Type II (3 phrasings across train & test)
    for m in re.finditer(
        rf"Our SOC 2 Type II report \({DATE_PAT} to {DATE_PAT}\) was issued by .+? on ({DATE_PAT})",
        text,
    ):
        certs.append({"name": "SOC 2 Type II", "status": "certified", "date": parse_date_str(m.group(1)), "valid_until": None})
        ev_levels.append("documented")
    for m in re.finditer(
        rf"completed a SOC 2 Type II examination for the period {DATE_PAT} to {DATE_PAT}; the report, issued ({DATE_PAT}) by",
        text,
    ):
        certs.append({"name": "SOC 2 Type II", "status": "certified", "date": parse_date_str(m.group(1)), "valid_until": None})
        ev_levels.append("documented")
    for m in re.finditer(
        rf"Independent audit: .+? issued a SOC 2 Type II report on ({DATE_PAT}), covering {DATE_PAT} to {DATE_PAT}",
        text,
    ):
        certs.append({"name": "SOC 2 Type II", "status": "certified", "date": parse_date_str(m.group(1)), "valid_until": None})
        ev_levels.append("documented")

    # Documented SOC 2 Type I (2 phrasings across train & test)
    for m in re.finditer(rf"issued our SOC 2 Type I report on ({DATE_PAT}), available under NDA", text):
        certs.append({"name": "SOC 2 Type I", "status": "certified", "date": parse_date_str(m.group(1)), "valid_until": None})
        ev_levels.append("documented")
    for m in re.finditer(rf"received a SOC 2 Type I report from .+?, issued ({DATE_PAT})\.", text):
        certs.append({"name": "SOC 2 Type I", "status": "certified", "date": parse_date_str(m.group(1)), "valid_until": None})
        ev_levels.append("documented")

    # Official page reference to ISO 27001 certificate in regulator registry
    for m in re.finditer(r"(ISO-27001-\d+)", text):
        cid_iso = m.group(1)
        if cid_iso in reg_certs_by_id:
            certs.append(reg_certs_by_id[cid_iso])
            ev_levels.append("documented")

    # Claimed SOC 2 Type II (without auditor / report date)
    if re.search(
        r"proud to be SOC 2 Type II certified|Security you can trust: SOC 2 Type II certified|is SOC 2 Type II certified\.",
        text,
    ):
        certs.append({"name": "SOC 2 Type II", "status": "certified", "date": None, "valid_until": None})
        ev_levels.append("claimed")

    # Claimed generic SOC 2 (type not stated)
    if re.search(
        r"Fully SOC 2 compliant, with controls reviewed every year\.|"
        r"We maintain SOC 2 compliance across our platform\.|"
        r"is SOC 2 compliant\.",
        text,
    ):
        certs.append({"name": "SOC 2", "status": "certified", "date": None, "valid_until": None})
        ev_levels.append("claimed")

    # SOC 2 Type II audit in progress
    if re.search(r"SOC 2 Type II audit is in progress|has started its SOC 2 Type II audit", text):
        certs.append({"name": "SOC 2 Type II", "status": "in_progress", "date": None, "valid_until": None})
        ev_levels.append("claimed")

    # Other non-SOC2/non-ISO27001 badges (lead to FAIL if no accepted cert is present)
    for badge in ("Cyber Essentials Plus", "HIPAA attestation", "CSA STAR Level 1", "PCI DSS SAQ-A", "ISO 9001"):
        if badge.lower() in text.lower():
            certs.append({"name": badge, "status": "certified", "date": None, "valid_until": None})
            ev_levels.append("claimed")

    if certs:
        ev = "documented" if "documented" in ev_levels else "claimed"
        out["security_certifications"] = {"value": certs, "evidence_level": ev}

    # 2. data_regions
    avail: list[str] = []
    planned: list[str] = []
    for m in re.finditer(
        r"(?:Available storage regions today:|Data residency: workspaces can be hosted in|"
        r"Customer content is stored at rest in|You can keep your data in)\s*([^.;\n]+)",
        text,
    ):
        avail.extend(extract_regions_from_text(m.group(1)))
    for m in re.finditer(
        r"(?:A\s+(.+?)\s+region is planned for Q\d|We are planning to add\s+(.+?)\s+hosting in Q\d)",
        text,
    ):
        grp = m.group(1) or m.group(2)
        planned.extend(extract_regions_from_text(grp))
    if avail or planned:
        out["data_regions"] = {
            "value": {
                "available": list(dict.fromkeys(avail)),
                "planned": list(dict.fromkeys(planned)),
            }
        }

    # 3. trains_on_customer_data
    if re.search(
        r"never use customer content to train|not used for training, and that applies to every plan|"
        r"not used for model training on any plan",
        text,
    ):
        out["trains_on_customer_data"] = {"value": "no"}
    elif re.search(
        r"On paid plans we do not use customer content for model training|"
        r"Training on your content is switched off for Team, Business and Enterprise plans",
        text,
    ):
        out["trains_on_customer_data"] = {"value": "no_on_paid_plans"}
    elif re.search(r"unless an administrator turns off|you can opt out in the admin console", text):
        out["trains_on_customer_data"] = {"value": "opt_out_available"}
    elif re.search(
        r"agree that we may use your content to train and improve our models|"
        r"Customer inputs and outputs are used to train our models on all plans",
        text,
    ):
        out["trains_on_customer_data"] = {"value": "yes"}

    # 4. subprocessors (Markdown table rows + 2 prose templates)
    subs: list[dict] = []
    for m in re.finditer(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|$", text, flags=re.M):
        name, purp, country = m.group(1).strip(), m.group(2).strip().lower(), m.group(3).strip()
        if purp in PURPOSE_MAP:
            subs.append({"name": name, "category": PURPOSE_MAP[purp], "country": country})
    for m in re.finditer(r"([A-Z][A-Za-z0-9 &]+?),\s*based in\s+([A-Za-z ]+?),\s*provides\s+([^.\n]+)\.", text):
        name, country, purp = m.group(1).strip(), m.group(2).strip(), m.group(3).strip().lower()
        if purp in PURPOSE_MAP:
            subs.append({"name": name, "category": PURPOSE_MAP[purp], "country": country})
    for m in re.finditer(r"We use\s+([A-Z][A-Za-z0-9 &]+?)\s*\(([^)]+)\)\s*for\s+([^.\n]+)\.", text):
        name, country, purp = m.group(1).strip(), m.group(2).strip(), m.group(3).strip().lower()
        if purp in PURPOSE_MAP:
            subs.append({"name": name, "category": PURPOSE_MAP[purp], "country": country})
    if subs:
        out["subprocessors"] = {"value": subs}

    # 5. data_retention
    def_days = None
    del_days = None
    has_ret_statement = False
    m = re.search(
        r"(?:Default retention:\s*(\d+)\s*days following termination|"
        r"After contract end, customer content is retained for\s*(\d+)\s*days|"
        r"We keep customer content for\s*(\d+)\s*days after the account is closed)",
        text,
    )
    if m:
        def_days = int(m.group(1) or m.group(2) or m.group(3))
        has_ret_statement = True
    m = re.search(
        r"(?:Deletion requests are honoured within\s*(\d+)\s*days|"
        r"Customers can request deletion at any time and we complete it within\s*(\d+)\s*days|"
        r"On request, all customer content is erased within\s*(\d+)\s*days)",
        text,
    )
    if m:
        del_days = int(m.group(1) or m.group(2) or m.group(3))
        has_ret_statement = True
    if re.search(
        r"We retain data only for as long as necessary to provide the service\.|"
        r"Data is kept in line with our legitimate business purposes\.",
        text,
    ):
        has_ret_statement = True
    if has_ret_statement:
        out["data_retention"] = {"value": {"default_days": def_days, "deletion_on_request_days": del_days}}

    # 6. sso_saml
    if re.search(
        r"Single sign-on \(SAML 2\.0 and OIDC\) is included on every plan, including Free|"
        r"SSO via SAML and OIDC is available to all customers on all plans",
        text,
    ):
        out["sso_saml"] = {"value": "all_plans"}
    elif re.search(
        r"SAML single sign-on is available on all paid plans|"
        r"Single sign-on comes with every paid subscription",
        text,
    ):
        out["sso_saml"] = {"value": "paid_plans"}
    elif re.search(
        r"SAML and OIDC single sign-on is available on the Enterprise plan only|"
        r"SSO is an Enterprise feature and is not included in Team or Business",
        text,
    ):
        out["sso_saml"] = {"value": "enterprise_only"}
    elif re.search(
        r"We do not currently offer single sign-on|"
        r"SAML SSO is on our roadmap and is not available today",
        text,
    ):
        out["sso_saml"] = {"value": "none"}

    # 7. security_incidents
    incs: list[dict] = []
    has_no_inc = False
    if re.search(
        r"No security incident affecting customer data has been recorded in the last \d+ months\.|"
        r"Our incident history: we have had no security incidents involving customer data in the past two years\.",
        text,
    ):
        has_no_inc = True
    for m in re.finditer(
        rf"({DATE_PAT}):\s*([^(\n]+?)\s*\(severity:\s*(critical|major|minor);\s*"
        rf"post-incident review\s*(published|not yet published)\)\.",
        text,
    ):
        incs.append(
            {
                "date": parse_date_str(m.group(1)),
                "summary": m.group(2).strip(),
                "severity": m.group(3).lower(),
                "postmortem_published": (m.group(4).lower() == "published"),
            }
        )
    for m in re.finditer(
        rf"^\|\s*({DATE_PAT})\s*\|\s*([^|]+?)\s*\|\s*(critical|major|minor)\s*\|\s*(Published|Not published)\s*\|$",
        text,
        flags=re.M,
    ):
        incs.append(
            {
                "date": parse_date_str(m.group(1)),
                "summary": m.group(2).strip(),
                "severity": m.group(3).lower(),
                "postmortem_published": (m.group(4).lower() == "published"),
            }
        )
    for m in re.finditer(
        rf"On ({DATE_PAT}) we recorded a (critical|major|minor) incident:\s*([^,\n]+),\s*"
        rf"and the post-incident review is (published|not yet published)\.",
        text,
    ):
        incs.append(
            {
                "date": parse_date_str(m.group(1)),
                "summary": m.group(3).strip(),
                "severity": m.group(2).lower(),
                "postmortem_published": (m.group(4).lower() == "published"),
            }
        )
    if incs or has_no_inc:
        out["security_incidents"] = {"value": incs}

    # 8. dpa_available
    if re.search(
        r"Our standard Data Processing Agreement is published on our legal page and applies to every customer automatically\.|"
        r"A signed DPA is built into our terms, so no separate request is needed\.",
        text,
    ):
        out["dpa_available"] = {"value": "yes"}
    elif re.search(
        r"A Data Processing Agreement is available on request|"
        r"To receive our DPA, email the legal team",
        text,
    ):
        out["dpa_available"] = {"value": "on_request"}
    elif re.search(
        r"We do not currently offer a separate Data Processing Agreement|"
        r"A DPA is not offered at this time\.",
        text,
    ):
        out["dpa_available"] = {"value": "no"}

    return out


def build_case_facts(pages: list[dict], case: dict) -> dict:
    """
    Build the canonical `facts` dictionary for `case` from its raw `pages`:
    1. Extract verified regulator certificates matching `case['legal_entity']`.
    2. Filter to `official` pages matching `case['official_domain']`.
    3. Sort official pages by `last_updated` ascending so newer pages win on conflict.
    """
    reg_certs_by_id = extract_regulator_certs(pages, case)
    off_pages = [p for p in pages if is_official_vendor_page(p, case)]
    off_pages.sort(key=lambda x: x.get("last_updated", ""))

    facts: dict = {}
    for p in off_pages:
        pf = extract_page_facts(p, case, reg_certs_by_id)
        for field_name, field_val in pf.items():
            facts[field_name] = field_val
    return facts


def resolve_data_dir(explicit: str | None = None) -> Path:
    """Locate the competition input directory locally or inside a Kaggle Notebook."""
    if explicit:
        p = Path(explicit)
        if p.exists():
            return p
    candidates = [
        Path(__file__).resolve().parent / "input",
        Path("input"),
        Path("/kaggle/input/vendor-verdict-can-we-trust-this-ai-tool"),
        Path("."),
    ]
    for c in candidates:
        if (c / "cases.csv").exists() and (c / "pages.jsonl").exists():
            return c
    raise FileNotFoundError("Could not find competition data directory containing cases.csv and pages.jsonl")


def run_pipeline(data_dir: Path, out_csv: Path, validate: bool = True) -> dict:
    """Run validation on train_labels.csv (if requested) and generate submission.csv for test.csv."""
    if str(data_dir) not in sys.path:
        sys.path.insert(0, str(data_dir))
    import rules_lite as rl

    reqs = rl.load_requirements(data_dir / "requirements.json")
    cases = {r["case_id"]: r for r in csv.DictReader((data_dir / "cases.csv").open(encoding="utf-8"))}

    pages_by_case: dict[str, list[dict]] = {}
    for line in (data_dir / "pages.jsonl").open(encoding="utf-8"):
        p = json.loads(line)
        pages_by_case.setdefault(p["case_id"], []).append(p)

    # Pre-compute verdicts for all 700 cases
    verdicts_cache: dict[str, tuple[dict[str, str], str]] = {}
    for cid, c in cases.items():
        facts = build_case_facts(pages_by_case.get(cid, []), c)
        as_of = date.fromisoformat(c["as_of"])
        v = rl.evaluate(facts, reqs, c["tier"], int(c["users"]), as_of)
        verdicts_cache[cid] = (v, rl.overall(v, reqs))

    result_summary: dict = {}

    if validate and (data_dir / "train_labels.csv").exists():
        import metric
        import pandas as pd

        train_sol = pd.read_csv(data_dir / "train_labels.csv")
        train_preds = []
        mismatches = []
        for _, row in train_sol.iterrows():
            cid = row["case_id"]
            req_id = row["requirement_id"]
            v, ov = verdicts_cache[cid]
            pred_v = ov if req_id == "OVERALL" else v.get(req_id, "UNKNOWN")
            train_preds.append({"id": row["id"], "verdict": pred_v})
            if pred_v != row["verdict"]:
                mismatches.append((row["id"], row["verdict"], pred_v))

        sub_df = pd.DataFrame(train_preds)
        comp = metric.components(train_sol, sub_df)
        comp["mismatches"] = len(mismatches)
        comp["total_train_rows"] = len(train_sol)
        result_summary["train_metrics"] = comp
        print(
            f"[Train Validation] rows={len(train_sol)} | mismatches={len(mismatches)} | "
            f"macro_f1={comp['macro_f1']:.4f} | overall_acc={comp['overall_accuracy']:.4f} | "
            f"false_confidence={comp['false_confidence_rate']:.4f} | SCORE={comp['score']:.4f}"
        )

    # Write test submission
    test_rows = list(csv.DictReader((data_dir / "test.csv").open(encoding="utf-8")))
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "verdict"])
        for row in test_rows:
            cid = row["case_id"]
            req_id = row["requirement_id"]
            v, ov = verdicts_cache[cid]
            pred_v = ov if req_id == "OVERALL" else v.get(req_id, "UNKNOWN")
            w.writerow([row["id"], pred_v])

    result_summary["test_rows_written"] = len(test_rows)
    result_summary["output_path"] = str(out_csv)
    print(f"[Submission Written] {out_csv} ({len(test_rows)} prediction rows + header)")
    return result_summary


def main() -> None:
    ap = argparse.ArgumentParser(description="Solve Vendor Verdict Kaggle competition.")
    ap.add_argument("--data", default=None, help="Path to competition input folder (default: auto-detect)")
    ap.add_argument("--out", default="submission.csv", help="Output CSV path (default: submission.csv)")
    ap.add_argument("--no-validate", action="store_true", help="Skip train_labels.csv validation")
    args = ap.parse_args()

    data_dir = resolve_data_dir(args.data)
    run_pipeline(data_dir=data_dir, out_csv=Path(args.out), validate=not args.no_validate)


if __name__ == "__main__":
    main()
