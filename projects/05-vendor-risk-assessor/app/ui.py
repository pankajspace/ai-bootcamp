"""
app/ui.py — Reviewer Workbench & Observability Console (Streamlit, Milestone 5).

Run:   streamlit run app/ui.py

Milestone 5 features:
  1. Streams node-by-node progress (`guard_input` → `route` → `vendor_research` → `match` → `questionnaire` → `human_gate` → `report`)
     with per-stage timings.
  2. Displays the trace as a structured tree beside the report so a reviewer can trace from a verdict to the source page.
  3. Provides a Human Gate Approve / Reject form that persists decisions to `AssessmentStore` (`runs/assessor.db`)
     and never offers an Approve option when a report is `BLOCKED`.
  4. Includes a Vendor History (`SEC-12.1`) tab and an Observability tab (last 20 runs with p50/p95 latency & cost).
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.api import IDENTITY_DIRECTORY  # noqa: E402
from assessor.config import SETTINGS  # noqa: E402
from assessor.graph import Pipeline, new_state  # noqa: E402
from assessor.questionnaire import as_email  # noqa: E402
from assessor.store import AssessmentStore  # noqa: E402
from assessor.tracing import Budget, Tracer  # noqa: E402

STAGE_ORDER = [
    "guard_input",
    "route",
    "policy_qa",
    "plan",
    "search",
    "identity_rejected",
    "quarantined",
    "evidence",
    "vendor_research",
    "match",
    "questionnaire",
    "human_gate",
    "report",
    "approval",
]


def build_trace_tree(events: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group flat trace.jsonl events into an ordered hierarchical tree by stage for the UI trace viewer."""
    tree: dict[str, list[dict[str, Any]]] = {}
    for ev in events:
        stage = ev.get("stage", "other")
        tree.setdefault(stage, []).append(ev)
    ordered: dict[str, list[dict[str, Any]]] = {}
    for s in STAGE_ORDER:
        if s in tree:
            ordered[s] = tree.pop(s)
    for k, v in tree.items():
        ordered[k] = v
    return ordered


def allowed_decisions_for_overall(overall: str) -> list[str]:
    """Milestone 5 rule: A BLOCKED report must not offer an Approve button."""
    if overall == "BLOCKED":
        return ["reject"]
    return ["approve", "reject"]


def render_app() -> None:
    import streamlit as st  # noqa: WPS433

    st.set_page_config(page_title="Vendor Risk Assessor — Nimbu Mart", layout="wide")
    st.title("AI Vendor Risk Assessor")
    st.caption(
        f"Nimbu Mart · LLM: {SETTINGS.llm_provider} · search: {SETTINGS.search_provider} · "
        "an input to the review, not an approval"
    )

    store = AssessmentStore()

    with st.sidebar:
        st.header("Caller Identity (Server ACL)")
        identity_options = [
            "priya.sec@nimbumart.example",
            "rohan.proc@nimbumart.example",
            "meera.dpo@nimbumart.example",
            "alice@nimbumart.example",
        ]
        caller_id = st.selectbox("Authenticated user", identity_options, index=0)
        groups = IDENTITY_DIRECTORY.get(caller_id, ["public", "employees"])
        st.caption(f"Server-derived groups: `{', '.join(groups)}`")

        st.divider()
        st.header("Assessment Scope")
        tier = st.selectbox("Highest data tier", ["T1", "T2", "T3"], index=2)
        users = st.number_input("Number of users", 1, 10000, 35)
        vendor = st.text_input("Vendor (optional, otherwise detected)", "")
        domain = st.text_input("Official domain (optional)", "")

    tab_assess, tab_history, tab_obs = st.tabs(
        ["🔍 Assess & Review", "📜 Vendor History (SEC-12.1)", "📊 Observability (Last 20 Runs)"]
    )

    with tab_assess:
        q = st.text_input("Question", "Can our support team use LedgerLens AI to summarise customer tickets?")
        if st.button("Run Assessment", type="primary"):
            SETTINGS.verbose = False
            tracer = Tracer("ui")
            pipe = Pipeline(tracer=tracer, budget=Budget(), store=store)
            progress_bar = st.progress(0, text="Starting pipeline…")
            step_names = ["guard_input", "route", "vendor_research", "match", "questionnaire", "human_gate", "report"]

            with st.status("Streaming pipeline execution…", expanded=True) as status_box:
                def _on_step(stage: str, _state: dict, dur_ms: float) -> None:
                    idx = step_names.index(stage) + 1 if stage in step_names else len(step_names)
                    pct = min(100, int((idx / len(step_names)) * 100))
                    progress_bar.progress(pct, text=f"Completed `{stage}` ({dur_ms:.1f} ms)")
                    status_box.write(f"✓ **{stage}** finished in `{dur_ms:.1f} ms`")

                s = pipe.run(
                    new_state(
                        q,
                        user_groups=groups,
                        tier=tier,
                        users=int(users),
                        vendor=vendor or None,
                        domain=domain or None,
                        requested_by=caller_id,
                    ),
                    on_step=_on_step,
                )
                status_box.update(label=f"Finished route `{s['route']}`", state="complete", expanded=False)
            tracer.close()
            st.session_state["last_run_id"] = tracer.run_id
            st.session_state["last_state"] = s
            st.session_state["last_events"] = list(tracer.events)

        last_state = st.session_state.get("last_state")
        last_run_id = st.session_state.get("last_run_id")
        if last_state is not None:
            rep_obj = last_state.get("report")
            if rep_obj is None:
                st.subheader(f"Route: `{last_state['route']}`")
                st.markdown(last_state["answer"])
            else:
                persisted = store.get_run(last_run_id) if last_run_id else None
                rep = persisted["report"] if persisted else rep_obj.model_dump(mode="json")
                events = persisted["trace"] if persisted else st.session_state.get("last_events", [])
                timings = persisted["stage_timings_ms"] if persisted else last_state.get("stage_timings_ms", {})

                col_report, col_trace = st.columns([3, 2], gap="large")
                with col_report:
                    colour = {"BLOCKED": "red", "CONDITIONAL": "orange", "READY_FOR_APPROVAL": "green"}[rep["overall"]]
                    st.markdown(f"### :{colour}[{rep['overall']}] — {rep['overall_reason']}")
                    st.caption(
                        f"Run `{rep['run_id']}` · {rep['llm_calls']} LLM calls · est. `${rep['cost_usd']:.4f}` · "
                        f"`{rep['duration_s']}s` · Approvers: {', '.join(rep['approval']['approver_roles'])}"
                    )
                    rows = [
                        {
                            "Requirement": r["title"],
                            "Clause": r["clause"],
                            "Verdict": r["verdict"],
                            "Severity": r["severity"],
                            "Reason": r["reason"],
                            "Evidence": ", ".join(r.get("evidence_urls", [])[:2]),
                            "As of": str(r.get("evidence_as_of") or ""),
                        }
                        for r in rep["results"]
                    ]
                    st.dataframe(rows, use_container_width=True, hide_index=True)

                    if rep.get("open_questions"):
                        st.subheader("Questions for the vendor")
                        for i, oq in enumerate(rep["open_questions"], 1):
                            st.markdown(f"**{i}. {oq['id']}** (`{oq['clause']}`) — {oq['question']}")
                        with st.expander("Copy-ready email to vendor"):
                            st.code(as_email(rep["request"]["vendor"], rep["open_questions"]), language="text")

                    st.divider()
                    st.subheader("Human Gate Decision (AI-5.1)")
                    cur_app = rep["approval"]
                    st.info(
                        f"Current status: **{cur_app['status'].upper()}**"
                        + (f" by **{cur_app['decided_by']}** on {cur_app['decided_on']}" if cur_app.get("decided_by") else "")
                        + (f" — *{cur_app['comment']}*" if cur_app.get("comment") else "")
                    )
                    allowed_decisions = allowed_decisions_for_overall(rep["overall"])
                    if rep["overall"] == "BLOCKED":
                        st.warning(
                            "This assessment is **BLOCKED** due to a failed blocking requirement. "
                            "Approval is disabled by the gate; you may only record a rejection or resolve the blocker first."
                        )
                    with st.form(key=f"decision_form_{rep['run_id']}"):
                        decision_choice = st.radio("Decision", allowed_decisions, horizontal=True)
                        approver_input = st.text_input("Approver name & role", value=caller_id)
                        comment_input = st.text_input("Decision rationale / conditions", value="")
                        submitted = st.form_submit_button("Record Human Decision")
                        if submitted:
                            try:
                                updated_app = store.record_decision(
                                    rep["run_id"],
                                    decision=decision_choice,
                                    approver=approver_input,
                                    comment=comment_input,
                                )
                                st.success(
                                    f"Recorded `{updated_app['status']}` by `{updated_app['decided_by']}` "
                                    f"on `{updated_app['decided_on']}`."
                                )
                                st.rerun()
                            except Exception as exc:  # noqa: BLE001
                                st.error(str(exc))

                    with st.expander("Full review file (Markdown)"):
                        st.markdown(persisted["report_md"] if persisted else last_state["answer"])

                with col_trace:
                    st.subheader("Trace Tree & Evidence Provenance")
                    if timings:
                        st.caption(
                            "Stage timings: "
                            + " · ".join(f"`{k}`: {v:.1f}ms" for k, v in timings.items())
                        )
                    tree = build_trace_tree(events)
                    for stage_name, stage_events in tree.items():
                        with st.expander(f"🌲 {stage_name} ({len(stage_events)} event{'s' if len(stage_events) != 1 else ''})", expanded=(stage_name in ("route", "identity_rejected", "quarantined", "match"))):
                            for ev in stage_events:
                                st.json(ev)
                    with st.expander("🔗 Verdict → Evidence URL Map", expanded=True):
                        for r in rep["results"]:
                            st.markdown(
                                f"- **`{r['requirement_id']}` ({r['verdict']})**: "
                                + (", ".join(r.get("evidence_urls", [])) if r.get("evidence_urls") else "*internal policy / no external URL*")
                            )

    with tab_history:
        st.subheader("Vendor Assessment History & Diffs (SEC-12.1)")
        hist_vendor = st.text_input("Vendor name", value=vendor or "LedgerLens AI", key="hist_vendor_input")
        hist = store.vendor_history(hist_vendor)
        st.caption(f"Total persisted assessments for **{hist['vendor']}**: `{hist['total_runs']}`")
        if not hist["runs"]:
            st.info("No runs stored for this vendor yet. Run an assessment in the first tab.")
        else:
            st.dataframe(
                [
                    {
                        "Run ID": r["run_id"],
                        "Created": r["created_at"],
                        "Tier": r["tier"],
                        "Outcome": r["overall"],
                        "Approval": r["approval_status"],
                        "Decided By": r["decided_by"] or "—",
                        "Changed Fields": ", ".join(r["fact_changes"].keys()) or "—",
                        "Changed Verdicts": ", ".join(r["verdict_changes"].keys()) or "—",
                    }
                    for r in reversed(hist["runs"])
                ],
                use_container_width=True,
                hide_index=True,
            )

    with tab_obs:
        st.subheader("Observability — Last 20 Runs (Production RAG Lab 13)")
        obs = store.observability_summary(limit=20)
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Runs Tracked", obs["count"])
        m2.metric("p50 Latency", f"{obs['latency_p50_s']:.2f}s")
        m3.metric("p95 Latency", f"{obs['latency_p95_s']:.2f}s")
        m4.metric("p50 Cost", f"${obs['cost_p50_usd']:.4f}")
        m5.metric("p95 Cost", f"${obs['cost_p95_usd']:.4f}")
        if obs["runs"]:
            st.dataframe(
                [
                    {
                        "Run ID": r["run_id"],
                        "Vendor": r["vendor"],
                        "Tier": r["tier"],
                        "Outcome": r["overall"],
                        "Approval": r["approval_status"],
                        "Latency (s)": r["duration_s"],
                        "Cost ($)": r["cost_usd"],
                        "LLM Calls": r["llm_calls"],
                        "Stage Timings (ms)": r["stage_timings_ms"],
                        "Timestamp": r["created_at"],
                    }
                    for r in obs["runs"]
                ],
                use_container_width=True,
                hide_index=True,
            )


if __name__ == "__main__":
    render_app()
