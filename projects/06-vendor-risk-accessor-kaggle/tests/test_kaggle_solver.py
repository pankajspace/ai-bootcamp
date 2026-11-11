"""
Tests for the Kaggle "Vendor Verdict: Can We Trust This AI Tool?" solver.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT / "input"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(INPUT_DIR) not in sys.path:
    sys.path.insert(0, str(INPUT_DIR))

import metric
import rules_lite as rl
import solve_kaggle as sk


def test_train_perfect_score(tmp_path: Path) -> None:
    """Solver must score 1.0000 (0 mismatches across all 3,185 rows) on train_labels.csv."""
    out_csv = tmp_path / "sub.csv"
    res = sk.run_pipeline(data_dir=INPUT_DIR, out_csv=out_csv, validate=True)
    tm = res["train_metrics"]
    assert tm["mismatches"] == 0
    assert tm["macro_f1"] == 1.0
    assert tm["overall_accuracy"] == 1.0
    assert tm["false_confidence_rate"] == 0.0
    assert tm["score"] == 1.0


def test_submission_file_contract() -> None:
    """Generated submission.csv must have 2,378 prediction rows + header and pass metric validation checks."""
    sub_path = ROOT / "submission.csv"
    assert sub_path.exists(), "submission.csv should exist in project root"

    sub_df = pd.read_csv(sub_path)
    test_df = pd.read_csv(INPUT_DIR / "test.csv")
    sample_df = pd.read_csv(INPUT_DIR / "sample_submission.csv")

    assert len(sub_df) == 2378
    assert list(sub_df.columns) == ["id", "verdict"]
    assert list(sub_df["id"]) == list(test_df["id"])

    # Verify metric.components accepts submission.csv without raising ParticipantVisibleError
    comp = metric.components(sample_df, sub_df)
    assert 0.0 <= comp["score"] <= 1.0


def test_lookalike_and_injection_quarantine() -> None:
    """Case c0002 (Garnforge AI) has a blog injection, a forum rumor, a look-alike GmbH, and an archived 2024 page."""
    cases = {r["case_id"]: r for r in csv.DictReader((INPUT_DIR / "cases.csv").open(encoding="utf-8"))}
    reqs = rl.load_requirements(INPUT_DIR / "requirements.json")
    pages = [
        json.loads(line)
        for line in (INPUT_DIR / "pages.jsonl").open(encoding="utf-8")
        if json.loads(line)["case_id"] == "c0002"
    ]
    c = cases["c0002"]
    facts = sk.build_case_facts(pages, c)

    # Blog claims India/US data regions, but official pages never state data_regions -> must be missing (UNKNOWN)
    assert "data_regions" not in facts
    # Archived 2024 page says DPA is not offered, but 2026 trust page says signed DPA is built into terms -> yes
    assert facts["dpa_available"]["value"] == "yes"
    # Archived 2024 page says paid_plans SSO, but 2026 help page says Enterprise plan only -> enterprise_only
    assert facts["sso_saml"]["value"] == "enterprise_only"

    verdicts = rl.evaluate(facts, reqs, c["tier"], int(c["users"]), c["as_of"])
    assert verdicts["DP-3.1"] == "UNKNOWN"
    assert verdicts["DP-2.2"] == "PASS"
    assert verdicts["SEC-7.1"] == "NEEDS_REVIEW"
