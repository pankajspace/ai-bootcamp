"""
eval/run_eval.py — score the assessor against data/gold_set.json (or data/gold_set_real.json),
calibrate and run the LLM-as-judge for verdict reasons, run the 4 component ablations, and print a scorecard.

COURSE MAP
  Deep Search    Module 10 & Lab 11 (evaluate the research, not just retrieval; gold set first; calibrated LLM-as-judge for reasons; ablations)
  Production RAG Module 10 & Lab 10 (golden dataset; retrieval + answer metrics; "make it a habit" — run this in CI)

Metrics
  verdict_accuracy     share of (case, requirement) verdicts equal to the gold verdict
  overall_accuracy     share of cases whose overall outcome matches
  field_accuracy       share of expected vendor profile facts matching gold (10 real vendors × 8 fields)
  reason_faithfulness  share of requirement verdict reasons judged faithful to cited evidence (calibrated on 20 items)
  guess_rate           PASS/FAIL where gold says UNKNOWN/NEEDS_REVIEW — the dangerous error; must be 0
  safety               quarantined / rejected / rumour-dropped URLs as expected (injection must never leak)
  policy_qa            clause/doc/content checks on policy questions; must_not_cite is a hard rule
  cost & time          per case

Usage
  python eval/run_eval.py                                       # full scorecard + ablations, writes reports/eval_report.md
  python eval/run_eval.py --strict                              # exit code 1 if any threshold fails (for CI)
  python eval/run_eval.py --gold data/gold_set_real.json --strict
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
from assessor.policy_rag import PolicyLibrary  # noqa: E402
from assessor.reason_judge import calibrate_reason_judge, judge_reason_faithfulness  # noqa: E402
from assessor.tracing import Budget  # noqa: E402
from assessor.vendor_research import VendorResearcher  # noqa: E402

THRESHOLDS = {
    "verdict_accuracy": 0.95,
    "overall_accuracy": 1.0,
    "field_accuracy": 0.80,
    "reason_faithfulness": 0.95,
    "guess_rate_max": 0.0,
    "safety": 1.0,
    "policy_qa_hard": 1.0,
}


def score_expected_facts(pf, exp_facts: dict) -> tuple[int, int]:
    """Compare extracted VendorProfile facts against gold expected_facts (Milestone 2 & 6 field_accuracy)."""
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


def _format_evidence_for_result(r, pf, req_to_field: dict[str, str]) -> str:
    """Build a concise evidence summary string from the exact VendorProfile field for judging a RequirementResult's reason."""
    field = req_to_field.get(r.requirement_id, "")
    if field == "approved_vendor_list" or r.requirement_id == "PROC-1.1":
        return f"approved_vendor_list policy_doc={r.policy_doc} clause={r.clause} verdict={r.verdict} {r.reason}"
    fact = pf.facts.get(field)
    if fact is not None:
        return f"{fact.field}={fact.value}; {fact.display}; evidence_level={fact.evidence_level}"
    return f"field={field} missing_fact=True verdict={r.verdict} {r.reason}"


def run_cases(pipe: Pipeline, gold: dict) -> dict:
    rows, n_ok, n_total, guesses, safety_checks, safety_ok, costs = [], 0, 0, 0, 0, 0, []
    facts_ok, facts_total = 0, 0
    reasons_ok, reasons_total = 0, 0
    overall_ok = 0
    for case in gold["cases"]:
        t0 = time.time()
        s = new_state(
            case["question"],
            user_groups=case["user_groups"],
            tier=case["tier"],
            users=case["users"],
            vendor=case["vendor"],
            domain=case.get("official_domain"),
        )
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

        # Milestone 6: Judge faithfulness of every applicable requirement verdict's reason
        req_to_field = {req.id: req.field for req in pipe.matcher.requirements}
        for r in rep.results:
            if r.verdict == "NOT_APPLICABLE":
                continue
            reasons_total += 1
            ev_str = _format_evidence_for_result(r, pf, req_to_field)
            j_res = judge_reason_faithfulness(r.verdict, r.reason, ev_str, llm=pipe.llm)
            reasons_ok += int(j_res.faithful)

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
        rows.append(
            {
                "case": case["id"],
                "overall": f"{rep.overall} ({'ok' if ov_ok else 'expected ' + case['expected_overall']})",
                "verdicts_ok": f"{len(case['expected_verdicts']) - len(mism)}/{len(case['expected_verdicts'])}",
                "mismatches": "; ".join(mism) or "—",
                "time_s": round(time.time() - t0, 2),
            }
        )
    return {
        "rows": rows,
        "verdict_accuracy": n_ok / max(1, n_total),
        "overall_accuracy": overall_ok / max(1, len(gold["cases"])),
        "field_accuracy": facts_ok / max(1, facts_total) if facts_total else 1.0,
        "reason_faithfulness": reasons_ok / max(1, reasons_total) if reasons_total else 1.0,
        "guess_rate": guesses / max(1, n_total),
        "safety": safety_ok / max(1, safety_checks) if safety_checks else 1.0,
        "safety_checks": safety_checks,
        "cost_usd": round(sum(costs), 4),
    }


def run_policy_questions(pipe: Pipeline, gold: dict) -> dict:
    rows, hard_total, hard_ok, soft_total, soft_ok = [], 0, 0, 0, 0
    for pq in gold.get("policy_questions", []):
        pa = pipe.library.answer(pq["question"], pq["user_groups"])
        cited_docs = {c.doc for c in pa.citations}
        top = pa.citations[0] if pa.citations else None
        checks = []
        if "must_not_cite_doc" in pq:
            ok = pq["must_not_cite_doc"] not in cited_docs
            hard_total += 1
            hard_ok += ok
            checks.append(("must_not_cite", ok))
        if "expected_clause" in pq:
            ok = top is not None and top.clause_id == pq["expected_clause"]
            soft_total += 1
            soft_ok += ok
            checks.append((f"top=={pq['expected_clause']}", ok))
        if "expected_doc" in pq:
            ok = top is not None and top.doc == pq["expected_doc"]
            soft_total += 1
            soft_ok += ok
            checks.append((f"doc=={pq['expected_doc'][:24]}", ok))
        for word in pq.get("expected_answer_contains", []):
            ok = (not pa.abstained) and word.lower() in pa.answer.lower()
            soft_total += 1
            soft_ok += ok
            checks.append((f"answer has '{word}'", ok))
        if pq.get("expected_abstain"):
            ok = pa.abstained
            soft_total += 1
            soft_ok += ok
            checks.append(("abstained", ok))
        rows.append(
            {
                "question": pq["id"],
                "known_to_fail": "yes" if pq.get("baseline_known_to_fail") else "",
                "checks": ", ".join(f"{'✓' if ok else '✗'} {n}" for n, ok in checks),
            }
        )
    return {
        "rows": rows,
        "policy_qa_hard": (hard_ok / hard_total) if hard_total else 1.0,
        "policy_qa_soft": (soft_ok / soft_total) if soft_total else 1.0,
    }


def run_ablations(gold: dict, real_gold: dict | None = None) -> list[dict]:
    """Milestone 6 (#3): Run one ablation per component (no reranker, no identity gate, no freshness decay, no planner)
    and return a comparison table proving each component earns its place."""
    target_gold = real_gold if real_gold is not None else gold
    configs = [
        ("Full System (M6 Baseline)", {"use_reranker": True, "enable_identity_gate": True, "enable_freshness_decay": True, "enable_planner": True}, "All components active"),
        ("No Reranker", {"use_reranker": False, "enable_identity_gate": True, "enable_freshness_decay": True, "enable_planner": True}, "pq-who-approves misses AI-5.1 without heading/intent reranking"),
        ("No Identity Gate", {"use_reranker": True, "enable_identity_gate": False, "enable_freshness_decay": True, "enable_planner": True}, "Look-alike UK/India domains leak into facts; safety drops"),
        ("No Freshness Decay", {"use_reranker": True, "enable_identity_gate": True, "enable_freshness_decay": False, "enable_planner": True}, "Stale 2024 page ties/beats 2026 trust centre on SSO & regions"),
        ("No Planner", {"use_reranker": True, "enable_identity_gate": True, "enable_freshness_decay": True, "enable_planner": False}, "Single generic query misses multi-page DPA/sub-processor/privacy facts"),
    ]
    ablation_rows = []
    for label, flags, impact in configs:
        lib = PolicyLibrary(use_reranker=flags["use_reranker"])
        pipe = Pipeline(tracer=None, budget=Budget(max_usd=10), library=lib)
        pipe.researcher = VendorResearcher(
            budget=pipe.budget,
            tracer=None,
            enable_planner=flags["enable_planner"],
            enable_identity_gate=flags["enable_identity_gate"],
            enable_freshness_decay=flags["enable_freshness_decay"],
        )
        c_res = run_cases(pipe, target_gold)
        p_res = run_policy_questions(pipe, gold)
        ablation_rows.append(
            {
                "config": label,
                "verdict_accuracy": c_res["verdict_accuracy"],
                "field_accuracy": c_res["field_accuracy"],
                "safety": c_res["safety"],
                "policy_qa_soft": p_res["policy_qa_soft"],
                "guess_rate": c_res["guess_rate"],
                "impact": impact,
            }
        )
    return ablation_rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--gold", default=str(GOLD_SET))
    ap.add_argument("--no-ablations", action="store_true")
    a = ap.parse_args(argv)
    SETTINGS.verbose = False
    gold_path = Path(a.gold)
    gold = json.loads(gold_path.read_text(encoding="utf-8"))

    t0 = time.time()
    pipe = Pipeline(tracer=None, budget=Budget(max_usd=10))
    res = run_cases(pipe, gold)
    pqs = run_policy_questions(pipe, gold)
    cal = calibrate_reason_judge(pipe.llm)

    lines = [
        f"# Evaluation report — {time.strftime('%Y-%m-%d %H:%M')}",
        "",
        f"LLM_PROVIDER={SETTINGS.llm_provider} · SEARCH_PROVIDER={SETTINGS.search_provider} · gold set: {gold_path.name}",
        "",
        "## Scorecard",
        "",
        "| Metric | Value | Threshold | Status |",
        "|---|---|---|---|",
    ]
    status = {}
    for metric, val, thr, higher in (
        ("verdict_accuracy", res["verdict_accuracy"], THRESHOLDS["verdict_accuracy"], True),
        ("overall_accuracy", res["overall_accuracy"], THRESHOLDS["overall_accuracy"], True),
        ("field_accuracy", res["field_accuracy"], THRESHOLDS["field_accuracy"], True),
        ("reason_faithfulness (LLM-as-judge)", res["reason_faithfulness"], THRESHOLDS["reason_faithfulness"], True),
        ("guess_rate", res["guess_rate"], THRESHOLDS["guess_rate_max"], False),
        ("safety", res["safety"], THRESHOLDS["safety"], True),
        ("policy_qa_hard (must_not_cite)", pqs["policy_qa_hard"], THRESHOLDS["policy_qa_hard"], True),
    ):
        ok = val >= thr if higher else val <= thr
        status[metric] = ok
        lines.append(f"| {metric} | {val:.2%} | {'≥' if higher else '≤'} {thr:.0%} | {'✅' if ok else '❌'} |")
    lines.append(f"| policy_qa_soft (clause/doc/content) | {pqs['policy_qa_soft']:.2%} | informational | — |")
    lines.append(
        f"| reason_judge_calibration (20 items) | {cal['accuracy']:.2%} (F1={cal['f1']:.2f}) | ≥ 90% | {'✅' if cal['accuracy'] >= 0.9 else '❌'} |"
    )
    lines.append(f"| cost (all cases) | ${res['cost_usd']:.4f} | — | — |")
    lines.append(f"| wall time | {time.time() - t0:.1f}s | — | — |")

    lines += ["", "## Assessment cases", "", "| Case | Overall | Verdicts | Mismatches | Time |", "|---|---|---|---|---|"]
    for r in res["rows"]:
        lines.append(f"| {r['case']} | {r['overall']} | {r['verdicts_ok']} | {r['mismatches']} | {r['time_s']}s |")

    if pqs["rows"]:
        lines += ["", "## Policy questions", "", "| Question | Baseline known to fail | Checks |", "|---|---|---|"]
        for r in pqs["rows"]:
            lines.append(f"| {r['question']} | {r['known_to_fail']} | {r['checks']} |")

    if not a.no_ablations:
        real_gold_path = ROOT / "data" / "gold_set_real.json"
        real_gold = json.loads(real_gold_path.read_text(encoding="utf-8")) if real_gold_path.exists() else None
        fictional_gold = json.loads(GOLD_SET.read_text(encoding="utf-8"))
        ablations = run_ablations(fictional_gold, real_gold=real_gold)
        lines += [
            "",
            "## Component Ablations (Milestone 6)",
            "",
            "| Configuration | Verdict Acc | Field Acc | Safety | Policy QA (Soft) | Guess Rate | What Degrades Without Component |",
            "|---|---|---|---|---|---|---|",
        ]
        for ab in ablations:
            lines.append(
                f"| {ab['config']} | {ab['verdict_accuracy']:.2%} | {ab['field_accuracy']:.2%} | "
                f"{ab['safety']:.2%} | {ab['policy_qa_soft']:.2%} | {ab['guess_rate']:.2%} | {ab['impact']} |"
            )

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
