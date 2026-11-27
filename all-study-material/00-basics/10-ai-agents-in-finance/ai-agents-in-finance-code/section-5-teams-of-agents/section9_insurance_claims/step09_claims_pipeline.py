"""
Section 9 lab — Auto-claims pipeline with seven agents (LlamaIndex AgentWorkflow)
================================================================================
Style: SEQUENTIAL PIPELINE WITH GUARDRAILS — compliance has the last word.

  FNOL → DocumentParser → Coverage → FraudScreener → Assessment → Decision → Compliance

    • Each agent has ONE tool. The tool reads only what the agent may see (DATA_ACCESS)
      and writes only the fields the agent owns (OWNED_FIELDS) — see step07_claims_rules.py.
    • Money and blocking decisions come from rules, never from free text.
    • Every step appends a PII-redacted line to the audit log.

How to run
----------
1. pip install llama-index-core llama-index-llms-openai pydantic python-dotenv
2. .env:   OPENAI_API_KEY=sk-...
3. python step09_claims_pipeline.py                # Sarah Chen's rear-end collision → APPROVE $3,800
   python step09_claims_pipeline.py --suspicious   # same claim, three fraud red flags → ESCALATE
   (no key? run  python step07_claims_rules.py  — the same stages without LLMs)

Cost: about 14–21 LLM calls per claim (each agent: tool call + short summary + handoff).
"""

import asyncio
import sys

from dotenv import load_dotenv
from llama_index.core.agent.workflow import AgentStream, AgentWorkflow, FunctionAgent, ToolCall
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI

import step07_claims_rules as R

load_dotenv()
MODEL = "gpt-4o"
llm = OpenAI(model=MODEL)

async def _load(ctx: Context, agent: str):
    """state = the shared whiteboard; view = ONLY the raw inputs this agent may see."""
    state = await ctx.store.get("state")
    inputs = await ctx.store.get("case_inputs")       # kept OUT of "state" on purpose
    return state, R.scoped_view(inputs, agent)


async def process_fnol(ctx: Context) -> str:
    """Create the claim record from the submitted claim form."""
    state, view = await _load(ctx, "FNOLAgent")       # sees the claim form only
    claim = R.fnol_intake(view["claim_form"])          # data never passes through the LLM
    state["claim"] = claim
    R.log_audit(state, "FNOLAgent", "claim created", f"type={claim['claim_type']}")
    await ctx.store.set("state", state)
    return f"FNOL processed. Claim {claim['claim_id']}, type {claim['claim_type']}."


async def parse_documents(ctx: Context) -> str:
    """Parse the submitted documents and list any missing ones."""
    state, view = await _load(ctx, "DocumentParser")
    r = R.parse_documents(view["submitted_documents"])
    R.write_fields(state["claim"], "DocumentParser", "parsing", **r)
    R.log_audit(state, "DocumentParser", "documents parsed", f"{len(r['parsed_documents'])} docs")
    await ctx.store.set("state", state)
    return (f"Parsed {len(r['parsed_documents'])} documents. Damage: {r['damage_description']}. "
            f"Missing: {r['missing_documents'] or 'none'}.")


async def verify_coverage(ctx: Context) -> str:
    """Check the claim against the policy sections and exclusions."""
    state, view = await _load(ctx, "CoverageAgent")
    r = R.verify_coverage(state["claim"], view["policy"])
    R.write_fields(state["claim"], "CoverageAgent", "coverage_check", **r)
    R.log_audit(state, "CoverageAgent", "coverage checked", r["coverage_reasoning"])
    await ctx.store.set("state", state)
    return r["coverage_reasoning"]


async def screen_for_fraud(ctx: Context) -> str:
    """Score the claim against the fraud red-flag rules."""
    state, view = await _load(ctx, "FraudScreener")   # policy dates + claims history only
    r = R.screen_for_fraud(view["policy"], state["claim"], view["claims_history"], view["fnol_date"])
    R.write_fields(state["claim"], "FraudScreener", "fraud_screening", **r)
    R.log_audit(state, "FraudScreener", "fraud screened", f"score={r['fraud_score']} flags={r['red_flags']}")
    await ctx.store.set("state", state)
    return (f"Fraud score {r['fraud_score']}/100. Flags: {r['red_flags'] or 'none'}. "
            f"Recommendation: {r['fraud_recommendation']}.")


async def assess_damage(ctx: Context) -> str:
    """Price the repair, apply the deductible and cap at the limit."""
    state, view = await _load(ctx, "AssessmentAgent")
    claim = state["claim"]
    r = R.assess_damage(view["claim_form"]["repair_items"], claim["deductible"], claim["applicable_limit"])
    R.write_fields(claim, "AssessmentAgent", "assessment", **r)
    R.log_audit(state, "AssessmentAgent", "damage assessed", r["assessment_breakdown"])
    await ctx.store.set("state", state)
    return r["assessment_breakdown"]


async def make_decision(ctx: Context) -> str:
    """Decide APPROVE / DENY / ESCALATE from the coverage, fraud and assessment results."""
    state, _ = await _load(ctx, "DecisionAgent")       # no raw inputs: the claim record only
    r = R.make_decision(state["claim"])
    R.write_fields(state["claim"], "DecisionAgent", R.STATUS_AFTER[r["decision"]], **r)
    R.log_audit(state, "DecisionAgent", f"decision {r['decision']}", r["decision_reasoning"])
    await ctx.store.set("state", state)
    return f"{r['decision']}: {r['decision_reasoning']}"


async def validate_compliance(ctx: Context) -> str:
    """Final guardrail: block the decision if any regulatory check fails."""
    state, _ = await _load(ctx, "ComplianceAgent")
    issues = R.validate_compliance(state["claim"])
    status = "blocked" if issues else "compliance_ok"
    R.write_fields(state["claim"], "ComplianceAgent", status, compliance_issues=issues)
    R.log_audit(state, "ComplianceAgent", "BLOCKED" if issues else "validated", str(issues or "compliant"))
    await ctx.store.set("state", state)
    return f"BLOCKED: {issues}" if issues else "Decision validated. Compliant."

def make_agent(name: str, job: str, tool, next_agent: str | None) -> FunctionAgent:
    hand = (f"then hand off to {next_agent} with a one-line reason."
            if next_agent else "then give the final answer yourself. Do not hand off.")
    return FunctionAgent(
        name=name,
        description=job,
        system_prompt=(
            f"You are the {name} of an auto-insurance claims team. Your job: {job} "
            f"Call {tool.__name__} EXACTLY ONCE. Report its result in one or two sentences "
            "without changing any number, decision or flag, " + hand),
        llm=llm,
        tools=[tool],
        can_handoff_to=[next_agent] if next_agent else [],
    )


PIPELINE = [   # (agent name, job, tool) in order
    ("FNOLAgent", "open the claim record from the first notice of loss.", process_fnol),
    ("DocumentParser", "turn the submitted documents into structured data.", parse_documents),
    ("CoverageAgent", "check what the policy covers for this loss.", verify_coverage),
    ("FraudScreener", "screen the claim for fraud red flags.", screen_for_fraud),
    ("AssessmentAgent", "estimate the payout within deductible and limit.", assess_damage),
    ("DecisionAgent", "decide APPROVE, DENY or ESCALATE.", make_decision),
    ("ComplianceAgent", "validate the decision before anything is paid.", validate_compliance),
]
AGENTS = [
    make_agent(name, job, tool, PIPELINE[i + 1][0] if i + 1 < len(PIPELINE) else None)
    for i, (name, job, tool) in enumerate(PIPELINE)
]

async def run_claim(case_inputs: dict, verbose: bool = True) -> dict:
    workflow = AgentWorkflow(
        agents=AGENTS, root_agent="FNOLAgent",
        initial_state={"claim": {}, "audit_log": []},  # AgentWorkflow pastes THIS into the
    )                                                   # first prompt — so no PII goes in it
    ctx = Context(workflow)
    await ctx.store.set("case_inputs", case_inputs)     # raw claim data: tools only
    handler = workflow.run(user_msg="A new auto claim was submitted. Process it.",
                           ctx=ctx, max_iterations=60)  # 7 agents × ~3 steps: 20 is too few
    last = None
    async for ev in handler.stream_events():
        if verbose and isinstance(ev, AgentStream) and ev.current_agent_name != last:
            last = ev.current_agent_name
            print(f"\n== {last} " + "=" * (50 - len(last)))
        if verbose and isinstance(ev, AgentStream) and ev.delta:
            print(ev.delta, end="", flush=True)
        if verbose and isinstance(ev, ToolCall) and ev.tool_name == "handoff":
            print(f"\n   🔀 → {ev.tool_kwargs.get('to_agent')}: {ev.tool_kwargs.get('reason')}")
    await handler
    return await ctx.store.get("state")


if __name__ == "__main__":
    inputs = R.sample_state(suspicious="--suspicious" in sys.argv)
    state = asyncio.run(run_claim(inputs))
    c = state["claim"]
    print(f"\n\nRESULT {c['claim_id']}: {c['decision']}  payout ${c['estimated_payout']:,.0f}  "
          f"fraud {c['fraud_score']}/100  gates {c['human_review_gates'] or 'none'}  "
          f"compliance {c['compliance_issues'] or 'OK'}")
    print("\nAudit log (append-only, PII redacted):")
    for row in state["audit_log"]:
        print(f"  {row['ts']}  {row['agent']:16} {row['action']:18} {row['details'][:90]}")
