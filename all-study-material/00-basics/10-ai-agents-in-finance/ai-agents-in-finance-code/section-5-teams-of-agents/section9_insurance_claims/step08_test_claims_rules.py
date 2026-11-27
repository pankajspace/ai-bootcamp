"""
Section 9 lab — invariant tests for the claims rules (free: no LLM, no API key)
==============================================================================
An LLM's wording changes every run, so we don't test wording. We test INVARIANTS:
statements that must be true for EVERY claim, whatever the agents say.

How to run:   python -m pytest step08_test_claims_rules.py -q
"""

import copy

import pytest

import step07_claims_rules as R


def run(**changes):
    """Run the whole pipeline offline on a copy of the sample, with some inputs changed."""
    state = copy.deepcopy(R.sample_state())
    for key, value in changes.items():
        if key == "repair_items":
            state["claim_form"] = {**state["claim_form"], "repair_items": value}
        else:
            state[key] = value
    return R.run_offline(state)["claim"]


def test_happy_path_matches_the_sample_run():
    c = run()
    assert (c["decision"], c["estimated_payout"], c["fraud_score"]) == ("APPROVE", 3800, 0)


@pytest.mark.parametrize("costs", [[100], [4_300], [80_000], [250_000]])
def test_payout_is_never_negative_and_never_above_the_limit(costs):
    c = run(repair_items=[{"item": "x", "cost": k} for k in costs])
    assert 0 <= c["estimated_payout"] <= c["applicable_limit"]


def test_a_fraud_flag_is_never_auto_approved():
    c = run(claims_history=[{}, {}, {}], fnol_date="2026-05-20")      # 20 + 15 = 35 → still fine
    assert c["fraud_score"] == 35 and c["decision"] == "APPROVE"
    c = run(policy={**R.SAMPLE_POLICY, "inception_date": "2026-03-20"},
            claims_history=[{}, {}, {}])                               # 25 + 20 = 45 > 40
    assert c["decision"] == "ESCALATE"


def test_missing_police_report_pauses_the_claim():
    docs = [d for d in R.SAMPLE_DOCUMENTS if d["type"] != "police_report"]
    c = run(submitted_documents=docs)
    assert c["decision"] == "ESCALATE" and "police_report" in c["missing_documents"]


def test_excluded_cause_is_denied_with_a_recognised_reason():
    form = {**R.SAMPLE_CLAIM_FORM, "description": "Collision during an amateur racing event; car hit a wall."}
    c = run(claim_form=form, submitted_documents=[form] + R.SAMPLE_DOCUMENTS[1:])
    assert c["decision"] == "DENY" and c["decision_reasoning"].startswith("EXCLUSION")
    assert c["compliance_issues"] == []


def test_compliance_blocks_short_reasoning_and_skipped_stages():
    c = run()
    c["decision_reasoning"] = "ok"
    c["stages_completed"].remove("FraudScreener")
    issues = R.validate_compliance(c)
    assert "Reasoning too short for an audit" in issues
    assert any("FraudScreener" in i for i in issues)


def test_no_personal_data_in_the_audit_log():
    state = R.run_offline(copy.deepcopy(R.sample_state()))
    text = str(state["audit_log"])
    assert "Sarah Chen" not in text and "FWS-AUTO-58213" not in text


def test_an_agent_cannot_write_another_agents_fields():
    claim = run()
    with pytest.raises(PermissionError):
        R.write_fields(claim, "AssessmentAgent", "assessment", fraud_score=0)
