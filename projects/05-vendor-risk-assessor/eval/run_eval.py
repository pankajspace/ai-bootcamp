"""
eval/run_eval.py — score the assessor against data/gold_set.json and print a scorecard.

COURSE MAP
  Deep Search    Module 10 (evaluate the research, not just the retrieval; gold set first; programmatic metrics)
  Production RAG Module 10 (golden dataset; retrieval + answer metrics; "make it a habit" — run this in CI)

Metrics
  verdict_accuracy     share of (case, requirement) verdicts equal to the gold verdict
  overall_accuracy     share of cases whose overall outcome matches
  guess_rate           PASS/FAIL where gold says UNKNOWN/NEEDS_REVIEW — the dangerous error; must be 0
  safety               quarantined / rejected / rumour-dropped URLs as expected (injection must never leak)
  policy_qa            clause/doc/content checks on policy questions; must_not_cite is a hard rule
  cost & time          per case (mock mode: $0)

Usage
  python eval/run_eval.py                 # full scorecard, writes reports/eval_report.md
  python eval/run_eval.py --strict        # exit code 1 if any threshold fails (for CI)

LEARNER TODO — Milestone 6
  * Add an LLM-as-judge metric for the *reasons* (are they faithful to the evidence?) — Deep Search Lab 11.
  * Add your real-vendor gold set (data/gold_set_real.json) and run live; keep the fictional one for CI.
  * Run an ablation: switch the identity gate off and watch the UK company's ISO certificate leak in.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from assessor.config import GOLD_SET, SETTINGS  # noqa: E402
from assessor.graph import Pipeline, new_state  # noqa: E402
from assessor.tracing import Budget  # noqa: E402

THRESHOLDS = {"verdict_accuracy": 0.95, "overall_accuracy": 1.0, "field_accuracy": 0.80, "guess_rate_max": 0.0, "safety": 1.0, "policy_qa_hard": 1.0}


def score_expected_facts(pf, exp_facts: dict) -> tuple[int, int]:
    """Compare extracted VendorProfile facts against gold expected_facts (Milestone 2 field_accuracy)."""
    ok_count, total_count = 0, 0
    for field, exp in (exp_facts or {}).items():
        total_count += 1
        fact = pf.facts.get(field)
        if exp is None:
            ok_count += int(fact is None or not fact.value)
            continue
        if fact is None:
            continue
        val = fact.value
        if field == "security_certifications":
            cert_names = {c.get("name") for c in (val or []) if c.get("status") == "certified"}
            has_ok = set(exp.get("has", [])) <= cert_names
            lvl_ok = fact.evidence_level == exp.get("evidence_level", fact.evidence_level)
            ok_count += int(has_ok and lvl_ok)
        elif field == "data_regions":
            avail = {x.lower() for x in (val or {}).get("available", [])}
            india_ok = ("india" in avail) == bool(exp.get("india_available", False))
            exp_avail = {x.lower() for x in exp.get("available", [])}
            ok_count += int(india_ok and (exp_avail <= avail))
        elif field == "subprocessors":
            cnt_ok = len(val or []) == exp.get("count", 0)
            mp_ok = any(i.get("category") == "model_provider" for i in (val or [])) == bool(exp.get("has_model_provider", False))
            ok_count += int(cnt_ok and mp_ok)
        elif field == "data_retention":
            ok_count += int(
                (val or {}).get("default_days") == exp.get("default_days")
                and (val or {}).get("deletion_on_request_days") == exp.get("deletion_on_request_days")
            )
        elif field == "security_incidents":
            majors = [i for i in (val or []) if str(i.get("severity", "")).lower() in ("major", "critical")]
            cnt_ok = len(majors) == exp.get("major_count", 0)
            pm_ok = all(bool(i.get("postmortem_published")) for i in majors) == bool(exp.get("all_major_have_postmortem", True))
            ok_count += int(cnt_ok and pm_ok)
        else:
            ok_count += int(val == exp)
    return ok_count, total_count


def run_cases(pipe: Pipeline, gold: dict) -> dict:
    rows, n_ok, n_total, guesses, safety_checks, safety_ok, costs = [], 0, 0, 0, 0, 0, []
    facts_ok, facts_total = 0, 0
    overall_ok = 0
    for case in gold["cases"]:
        t0 = time.time()
        s = new_state(case["question"], user_groups=case["user_groups"], tier=case["tier"], users=case["users"],
                      vendor=case["vendor"], domain=case.get("official_domain"))
        s = pipe.run_plain(s)
        rep = s["report"]
        got = {r.requirement_id: r.verdict for r in rep.results}
        mism = []
        for rid, exp in case["expected_verdicts"].items():
            n_total += 1
            if got.get(rid) == exp:
                n_ok += 1
            else:
                mism.append(f"{rid}: expected {exp}, got {got.get(rid)}")
            if exp in ("UNKNOWN", "NEEDS_REVIEW") and got.get(rid) in ("PASS", "FAIL"):
                guesses += 1
        ov_ok = rep.overall == case["expected_overall"]
        overall_ok += ov_ok
        pf = rep.profile
        f_ok, f_tot = score_expected_facts(pf, case.get("expected_facts", {}))
        facts_ok += f_ok
        facts_total += f_tot
        for key, attr in (("expected_quarantined_urls", pf.quarantined), ("expected_rejected_urls", pf.rejected)):
            for url in case.get(key, []):
                safety_checks += 1
                safety_ok += url in attr
        for url in case.get("expected_dropped_rumour_urls", []):
            safety_checks += 1
            safety_ok += any(url in d for d in pf.dropped)
        # the injection page's claims must never be used as evidence
        for url in case.get("expected_quarantined_urls", []):
            safety_checks += 1
            safety_ok += not any(url in r.evidence_urls for r in rep.results)
        costs.append(pipe.budget.spent_usd)
        rows.append({"case": case["id"], "overall": f"{rep.overall} ({'ok' if ov_ok else 'expected ' + case['expected_overall']})",
                     "verdicts_ok": f"{len(case['expected_verdicts']) - len(mism)}/{len(case['expected_verdicts'])}",
                     "mismatches": "; ".join(mism) or "—", "time_s": round(time.time() - t0, 2)})
    return {"rows": rows, "verdict_accuracy": n_ok / max(1, n_total), "overall_accuracy": overall_ok / max(1, len(gold["cases"])),
            "field_accuracy": facts_ok / max(1, facts_total) if facts_total else 1.0,
            "guess_rate": guesses / max(1, n_total), "safety": safety_ok / max(1, safety_checks) if safety_checks else 1.0, "safety_checks": safety_checks,
            "cost_usd": round(sum(costs), 4)}


def run_policy_questions(pipe: Pipeline, gold: dict) -> dict:
    rows, hard_total, hard_ok, soft_total, soft_ok = [], 0, 0, 0, 0
    for pq in gold.get("policy_questions", []):
        pa = pipe.library.answer(pq["question"], pq["user_groups"])
        cited_docs = {c.doc for c in pa.citations}
        cited_clauses = {c.clause_id for c in pa.citations}
        top = pa.citations[0] if pa.citations else None
        checks = []
        if "must_not_cite_doc" in pq:
            ok = pq["must_not_cite_doc"] not in cited_docs
            hard_total += 1; hard_ok += ok
            checks.append(("must_not_cite", ok))
        if "expected_clause" in pq:
            ok = top is not None and top.clause_id == pq["expected_clause"]
            soft_total += 1; soft_ok += ok
            checks.append((f"top=={pq['expected_clause']}", ok))
        if "expected_doc" in pq:
            ok = top is not None and top.doc == pq["expected_doc"]
            soft_total += 1; soft_ok += ok
            checks.append((f"doc=={pq['expected_doc'][:24]}", ok))
        for word in pq.get("expected_answer_contains", []):
            ok = (not pa.abstained) and word.lower() in pa.answer.lower()
            soft_total += 1; soft_ok += ok
            checks.append((f"answer has '{word}'", ok))
        if pq.get("expected_abstain"):
            ok = pa.abstained
            soft_total += 1; soft_ok += ok
            checks.append(("abstained", ok))
        rows.append({"question": pq["id"], "known_to_fail": "yes" if pq.get("baseline_known_to_fail") else "",
                     "checks": ", ".join(f"{'✓' if ok else '✗'} {n}" for n, ok in checks)})
    return {"rows": rows, "policy_qa_hard": (hard_ok / hard_total) if hard_total else 1.0,
            "policy_qa_soft": (soft_ok / soft_total) if soft_total else 1.0}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--gold", default=str(GOLD_SET))
    a = ap.parse_args(argv)
    SETTINGS.verbose = False
    gold = json.loads(Path(a.gold).read_text(encoding="utf-8"))

    t0 = time.time()
    pipe = Pipeline(tracer=None, budget=Budget(max_usd=10))
    res = run_cases(pipe, gold)
    pqs = run_policy_questions(pipe, gold)

    lines = [f"# Evaluation report — {time.strftime('%Y-%m-%d %H:%M')}", "",
             f"LLM_PROVIDER={SETTINGS.llm_provider} · SEARCH_PROVIDER={SETTINGS.search_provider} · gold set: {Path(a.gold).name}", "",
             "## Scorecard", "", "| Metric | Value | Threshold | Status |", "|---|---|---|---|"]
    status = {}
    for metric, val, thr, higher in (("verdict_accuracy", res["verdict_accuracy"], THRESHOLDS["verdict_accuracy"], True),
                                      ("overall_accuracy", res["overall_accuracy"], THRESHOLDS["overall_accuracy"], True),
                                      ("field_accuracy", res["field_accuracy"], THRESHOLDS["field_accuracy"], True),
                                      ("guess_rate", res["guess_rate"], THRESHOLDS["guess_rate_max"], False),
                                      ("safety", res["safety"], THRESHOLDS["safety"], True),
                                      ("policy_qa_hard (must_not_cite)", pqs["policy_qa_hard"], THRESHOLDS["policy_qa_hard"], True)):
        ok = val >= thr if higher else val <= thr
        status[metric] = ok
        lines.append(f"| {metric} | {val:.2%} | {'≥' if higher else '≤'} {thr:.0%} | {'✅' if ok else '❌'} |")
    lines.append(f"| policy_qa_soft (clause/doc/content) | {pqs['policy_qa_soft']:.2%} | informational | — |")
    lines.append(f"| cost (all cases) | ${res['cost_usd']:.4f} | — | — |")
    lines.append(f"| wall time | {time.time() - t0:.1f}s | — | — |")
    lines += ["", "## Assessment cases", "", "| Case | Overall | Verdicts | Mismatches | Time |", "|---|---|---|---|---|"]
    for r in res["rows"]:
        lines.append(f"| {r['case']} | {r['overall']} | {r['verdicts_ok']} | {r['mismatches']} | {r['time_s']}s |")
    lines += ["", "## Policy questions", "", "| Question | Baseline known to fail | Checks |", "|---|---|---|"]
    for r in pqs["rows"]:
        lines.append(f"| {r['question']} | {r['known_to_fail']} | {r['checks']} |")
    report = "\n".join(lines)
    out = ROOT / "reports"
    out.mkdir(exist_ok=True)
    (out / "eval_report.md").write_text(report, encoding="utf-8")
    print(report)
    print(f"\nWritten to {out / 'eval_report.md'}")
    failed = [m for m, ok in status.items() if not ok]
    if a.strict and failed:
        print(f"\nFAILED thresholds: {failed}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
