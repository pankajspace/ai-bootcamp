"""Milestone 6: Evaluation, 10-vendor real gold set, calibrated LLM-as-judge for verdict reasons,
4-component ablation table, CI workflow, and demo script tests.
"""

from __future__ import annotations

import json

from assessor.config import GOLD_SET, ROOT
from assessor.graph import Pipeline
from assessor.reason_judge import (
    REASON_CALIBRATION_20,
    calibrate_reason_judge,
    judge_reason_faithfulness,
)
from assessor.tracing import Budget
from eval.run_eval import run_ablations, run_cases


def test_real_vendor_gold_set_has_10_vendors_x_8_fields_and_scores_100_percent():
    """Milestone 6 (#1): Real-vendor gold set has 10 vendors × 8 fields and passes all evaluation thresholds."""
    real_gold_path = ROOT / "data" / "gold_set_real.json"
    real_gold = json.loads(real_gold_path.read_text(encoding="utf-8"))
    assert len(real_gold["cases"]) == 10

    for case in real_gold["cases"]:
        assert len(case["expected_facts"]) == 8, f"{case['id']} should specify 8 expected_facts"

    pipe = Pipeline(tracer=None, budget=Budget(max_usd=10))
    res = run_cases(pipe, real_gold)
    assert res["field_accuracy"] >= 0.80
    assert res["verdict_accuracy"] >= 0.95
    assert res["overall_accuracy"] == 1.0
    assert res["guess_rate"] == 0.0
    assert res["safety"] == 1.0
    assert res["reason_faithfulness"] >= 0.95


def test_reason_judge_calibrated_on_20_hand_labelled_examples():
    """Milestone 6 (#2): Calibrate the LLM-as-judge on 20 hand-labelled reasons before scoring."""
    assert len(REASON_CALIBRATION_20) == 20
    cal = calibrate_reason_judge()
    assert cal["accuracy"] >= 0.90
    assert cal["f1"] >= 0.90

    # Spot-check a faithful and an unfaithful reason directly
    ok = judge_reason_faithfulness(
        "FAIL",
        "India is only 'planned' (available: ['US', 'EU'], planned: ['India']).",
        "available: ['US', 'EU'], planned: ['India']; evidence_level=documented",
    )
    assert ok.faithful is True

    bad = judge_reason_faithfulness(
        "PASS",
        "Vendor stores customer data in Mumbai, India data centers today.",
        "available: ['US', 'EU'], planned: ['India']; evidence_level=documented",
    )
    assert bad.faithful is False


def test_four_component_ablations_prove_each_component_earns_its_place():
    """Milestone 6 (#3): Run one ablation per component (no reranker, no identity gate, no freshness decay, no planner)
    and verify each ablation degrades its corresponding metric compared to the Full System."""
    fictional_gold = json.loads(GOLD_SET.read_text(encoding="utf-8"))
    real_gold = json.loads((ROOT / "data" / "gold_set_real.json").read_text(encoding="utf-8"))
    rows = {r["config"]: r for r in run_ablations(fictional_gold, real_gold=real_gold)}

    full = rows["Full System (M6 Baseline)"]
    assert full["verdict_accuracy"] == 1.0
    assert full["field_accuracy"] == 1.0
    assert full["safety"] == 1.0
    assert full["policy_qa_soft"] == 1.0
    assert full["guess_rate"] == 0.0

    # 1. No Reranker degrades Policy QA accuracy
    assert rows["No Reranker"]["policy_qa_soft"] < full["policy_qa_soft"]
    # 2. No Identity Gate degrades Safety and Field/Verdict accuracy
    assert rows["No Identity Gate"]["safety"] < full["safety"]
    assert rows["No Identity Gate"]["field_accuracy"] < full["field_accuracy"]
    # 3. No Freshness Decay degrades Field and Verdict accuracy on stale-vs-fresh conflicts
    assert rows["No Freshness Decay"]["field_accuracy"] < full["field_accuracy"]
    assert rows["No Freshness Decay"]["verdict_accuracy"] < full["verdict_accuracy"]
    # 4. No Planner degrades Field and Verdict accuracy on multi-page vendor profiles
    assert rows["No Planner"]["field_accuracy"] < full["field_accuracy"]
    assert rows["No Planner"]["verdict_accuracy"] < full["verdict_accuracy"]


def test_ci_workflow_and_demo_script_exist():
    """Milestone 6 (#4 & #5): Verify GitHub Actions CI workflow and demo script are present."""
    ci_path = ROOT / ".github" / "workflows" / "ci.yml"
    assert ci_path.exists()
    ci_text = ci_path.read_text(encoding="utf-8")
    assert "pytest" in ci_text
    assert "eval/run_eval.py --strict" in ci_text

    demo_path = ROOT / "scripts" / "run_demo.py"
    assert demo_path.exists()
