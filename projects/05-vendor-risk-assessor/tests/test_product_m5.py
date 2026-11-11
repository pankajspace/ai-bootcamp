"""Milestone 5: Product tests — LangGraph checkpointer + human_gate interrupt(),
FastAPI background queue, server-derived ACL user_groups, persistent database + vendor history (SEC-12.1),
BLOCKED approval refusal, observability (p50/p95 latency & cost), and UI helpers.
"""

from __future__ import annotations

import time

from fastapi.testclient import TestClient

from app.api import STORE, app
from app.ui import allowed_decisions_for_overall, build_trace_tree
from assessor.graph import Pipeline, new_state
from assessor.store import AssessmentStore
from assessor.tracing import Tracer


def test_langgraph_checkpointer_interrupts_at_human_gate_and_resumes():
    """Milestone 5 (#1): LangGraph checkpointer + `interrupt()` pauses at `human_gate` and resumes when decided."""
    pipe = Pipeline()
    state = new_state(
        "Can the product team use Parakeet Translate for internal roadmap docs?",
        user_groups=["public", "employees", "security"],
        tier="T2",
        users=20,
        vendor="Parakeet Translate",
    )
    paused_state, graph, config = pipe.start_checkpointed(state, thread_id="m5-parakeet-t2")

    # Execution paused right at human_gate before generating the final report
    snapshot = graph.get_state(config)
    assert snapshot.next == ("human_gate",)
    assert paused_state.get("report") is None
    assert paused_state["overall"] == "READY_FOR_APPROVAL"

    # Approver resumes the checkpoint days later
    final_state = pipe.resume_checkpointed(
        graph,
        config,
        decision="approve",
        approver="priya.sec@nimbumart.example",
        comment="T2 internal docs approved after reviewing Certis ISO 27001 entry.",
    )
    assert final_state["report"] is not None
    assert final_state["approval"].status == "approved"
    assert final_state["approval"].decided_by == "priya.sec@nimbumart.example"


def test_langgraph_checkpointer_refuses_approve_when_blocked():
    """Milestone 5 (#1 & #4): Resuming a BLOCKED checkpoint with `decision='approve'` is refused by `human_gate`."""
    pipe = Pipeline()
    state = new_state(
        "Can our support team use LedgerLens AI to summarise customer tickets?",
        user_groups=["public", "employees", "security"],
        tier="T3",
        users=40,
        vendor="LedgerLens AI",
    )
    paused_state, graph, config = pipe.start_checkpointed(state, thread_id="m5-ledgerlens-t3")
    assert paused_state["overall"] == "BLOCKED"

    final_state = pipe.resume_checkpointed(
        graph,
        config,
        decision="approve",
        approver="priya.sec@nimbumart.example",
        comment="Trying to force approval",
    )
    assert final_state["approval"].status == "pending"
    assert "Approval refused by the gate" in (final_state["approval"].comment or "")


def test_api_derives_user_groups_from_server_identity_never_request_body():
    """Milestone 5 (#3): Server derives `user_groups` from caller identity and ignores client-supplied groups."""
    client = TestClient(app)

    # 1. Unprivileged caller tries to spoof `user_groups: ["security", "procurement"]` in the JSON body
    r_spoof = client.post(
        "/ask",
        headers={"X-User-Identity": "alice@nimbumart.example"},
        json={
            "question": "Which vendors are on the approved vendor list?",
            "user_groups": ["public", "employees", "security", "procurement"],
        },
    )
    assert r_spoof.status_code == 200
    data_spoof = r_spoof.json()
    assert data_spoof["user_groups"] == ["public", "employees"]
    cited_docs_spoof = {c["doc"] for c in data_spoof["citations"]}
    assert "approved_vendor_list.md" not in cited_docs_spoof

    # 2. Authenticated Security reviewer gets server-derived `security` group and can read the AVL
    r_sec = client.post(
        "/ask",
        headers={"X-User-Identity": "priya.sec@nimbumart.example"},
        json={"question": "Which tier is Parakeet Translate approved for?"},
    )
    assert r_sec.status_code == 200
    data_sec = r_sec.json()
    assert "security" in data_sec["user_groups"]
    cited_docs_sec = {c["doc"] for c in data_sec["citations"]}
    assert "approved_vendor_list.md" in cited_docs_sec


def test_api_queued_assess_and_approval_persistence_across_restart():
    """Milestone 5 (#2 & #4): `/jobs/assess` queues a job, polls `/jobs/{job_id}`, refuses approval on BLOCKED,
    records approval on READY_FOR_APPROVAL, and persists across a fresh `AssessmentStore` instance."""
    client = TestClient(app)

    # 1. Enqueue a BLOCKED vendor assessment (LedgerLens AI at T3)
    enq = client.post(
        "/jobs/assess",
        headers={"X-User-Identity": "priya.sec@nimbumart.example"},
        json={
            "question": "Can our support team use LedgerLens AI to summarise customer tickets?",
            "vendor": "LedgerLens AI",
            "tier": "T3",
            "users": 35,
        },
    )
    assert enq.status_code == 200
    job_id = enq.json()["job_id"]

    # Poll until completed
    job_data = None
    for _ in range(30):
        poll = client.get(f"/jobs/{job_id}")
        assert poll.status_code == 200
        job_data = poll.json()
        if job_data["status"] == "completed":
            break
        time.sleep(0.05)

    assert job_data is not None and job_data["status"] == "completed"
    blocked_run_id = job_data["run_id"]
    assert len(job_data["progress"]) >= 5  # Streamed node stages recorded on the job

    # Attempting to approve a BLOCKED run returns HTTP 409 Conflict
    bad_app = client.post(
        f"/approve/{blocked_run_id}",
        json={"decision": "approve", "approver": "priya.sec@nimbumart.example", "comment": "Force"},
    )
    assert bad_app.status_code == 409

    # 2. Run a READY_FOR_APPROVAL assessment (Parakeet Translate at T2) and approve it
    ok_res = client.post(
        "/assess",
        headers={"X-User-Identity": "priya.sec@nimbumart.example"},
        json={
            "question": "Can the product team use Parakeet Translate for internal docs?",
            "vendor": "Parakeet Translate",
            "tier": "T2",
            "users": 15,
        },
    )
    assert ok_res.status_code == 200
    ready_run_id = ok_res.json()["run_id"]

    good_app = client.post(
        f"/approve/{ready_run_id}",
        json={
            "decision": "approve",
            "approver": "priya.sec@nimbumart.example",
            "comment": "Approved for T2 internal documentation.",
        },
    )
    assert good_app.status_code == 200
    assert good_app.json()["status"] == "approved"

    # Simulate server restart by opening a brand-new AssessmentStore on the same SQLite DB file
    restarted_store = AssessmentStore(STORE.db_path)
    persisted = restarted_store.get_run(ready_run_id)
    assert persisted is not None
    assert persisted["approval_status"] == "approved"
    assert persisted["decided_by"] == "priya.sec@nimbumart.example"


def test_api_vendor_history_diffs_and_observability_p50_p95():
    """Milestone 5 (#2 & #5): `/vendors/{name}/history` tracks changes across runs (SEC-12.1)
    and `/observability/runs` reports p50/p95 latency, cost, and stage timings (Lab 13)."""
    client = TestClient(app)

    # Run Parakeet Translate at T3 (CONDITIONAL) after running at T2 (READY_FOR_APPROVAL) to generate a verdict diff
    client.post(
        "/assess",
        headers={"X-User-Identity": "priya.sec@nimbumart.example"},
        json={
            "question": "Can our support team use Parakeet Translate for T3 live customer chats?",
            "vendor": "Parakeet Translate",
            "tier": "T3",
            "users": 40,
        },
    )

    hist_res = client.get("/vendors/Parakeet Translate/history")
    assert hist_res.status_code == 200
    hist = hist_res.json()
    assert hist["total_runs"] >= 2
    assert any(r["verdict_changes"] or r["overall_changed"] for r in hist["runs"][1:])

    obs_res = client.get("/observability/runs?limit=20")
    assert obs_res.status_code == 200
    obs = obs_res.json()
    assert obs["count"] >= 2
    assert "latency_p50_s" in obs and "latency_p95_s" in obs
    assert "cost_p50_usd" in obs and "cost_p95_usd" in obs
    assert obs["runs"][0]["stage_timings_ms"]


def test_ui_trace_tree_and_blocked_button_guard():
    """Milestone 5 (#4): UI helper functions group trace events into a stage tree and block Approve on BLOCKED."""
    assert allowed_decisions_for_overall("BLOCKED") == ["reject"]
    assert allowed_decisions_for_overall("CONDITIONAL") == ["approve", "reject"]
    assert allowed_decisions_for_overall("READY_FOR_APPROVAL") == ["approve", "reject"]

    tracer = Tracer("ui-test", enabled=False)
    pipe = Pipeline(tracer=tracer)
    pipe.run_plain(
        new_state(
            "Can our support team use LedgerLens AI to summarise customer tickets?",
            user_groups=["public", "employees", "security"],
            tier="T3",
            users=40,
        )
    )
    tree = build_trace_tree(tracer.events)
    assert "guard_input" in tree
    assert "route" in tree
    assert "identity_rejected" in tree
    assert "quarantined" in tree
    assert "match" in tree
