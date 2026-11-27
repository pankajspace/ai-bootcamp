"""
Section 9 lab — extension: adversarial fraud investigation (LlamaIndex AgentWorkflow)
====================================================================================
Style: PEER-TO-PEER DEBATE, triggered only when the pipeline escalates a fraud flag.

  FraudAdvocate ──► LegitimacyAdvocate ──► InvestigationDecision
  (argues fraud)    (argues legitimate,     (weighs both → a REFERRAL, never a verdict
                     sees the opening)        of fraud: that is a legal conclusion)

How to run
----------
    python step10_fraud_investigation.py            # runs the suspicious claim through it
Needs OPENAI_API_KEY in .env. Cost: about 9–12 LLM calls.
"""

import asyncio
from typing import Literal

from dotenv import load_dotenv
from llama_index.core.agent.workflow import AgentStream, AgentWorkflow, FunctionAgent
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

import step07_claims_rules as R

load_dotenv()
llm = OpenAI(model="gpt-4o")


class FraudArgument(BaseModel):
    position: Literal["fraud", "legitimate"]
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str]
    reasoning: str
    weaknesses: list[str]          # each side must name the holes in its OWN case


Referral = Literal["strong_fraud_indicators", "likely_fraud", "inconclusive", "likely_legitimate"]
ROUTING = {                        # code, not the LLM, decides where the claim goes next
    "strong_fraud_indicators": "Refer to the Special Investigations Unit (SIU)",
    "likely_fraud": "Flag for human review by a senior adjuster",
    "inconclusive": "Resume with caution: adjuster double-checks before payment",
    "likely_legitimate": "Clear the flag and resume normal processing",
}

async def get_case_file(ctx: Context) -> str:
    """Return the evidence both advocates must argue from (no personal data)."""
    claim = (await ctx.store.get("case"))["claim"]    # the escalated claim, tools only
    return (f"Claim {claim['claim_id']} ({claim['claim_type']}), loss {claim['date_of_loss']}.\n"
            f"Description: {R.redact(claim['description'], claim)}\n"
            f"Fraud score: {claim['fraud_score']}/100. Red flags: {claim['red_flags']}\n"
            f"Coverage: {claim['coverage_reasoning']}\n"
            f"Documents: {[d['type'] for d in claim['parsed_documents']]}; "
            f"damage: {claim['damage_description']}\nPayout at stake: ${claim['estimated_payout']:,.0f}")


async def submit_argument(ctx: Context, position: str, confidence: float,
                          evidence: list[str], reasoning: str, weaknesses: list[str]) -> str:
    """Save your structured argument. position must be 'fraud' or 'legitimate'; confidence 0-1."""
    try:
        arg = FraudArgument(position=position, confidence=confidence, evidence=evidence,
                            reasoning=reasoning, weaknesses=weaknesses)
    except ValidationError as e:                       # the LLM gets the error and can retry
        return f"REJECTED, fix and resubmit: {e.errors()[0]['msg']}"
    state = await ctx.store.get("state")
    state["arguments"][arg.position] = arg.model_dump()
    await ctx.store.set("state", state)
    return f"{arg.position} argument saved (confidence {arg.confidence:.2f})."


async def produce_fraud_determination(ctx: Context, referral: Referral,
                                      confidence: float, rationale: str) -> str:
    """Record the referral signal after BOTH arguments are in."""
    if referral not in ROUTING:                          # the type hint shapes the schema the
        return f"REJECTED: referral must be one of {list(ROUTING)}"   # LLM sees; it doesn't CHECK
    state = await ctx.store.get("state")
    if set(state["arguments"]) != {"fraud", "legitimate"}:   # guardrail: hear both sides
        return "REFUSED: both the fraud and the legitimacy arguments are required first."
    state["determination"] = {"referral": referral, "confidence": confidence,
                              "rationale": rationale, "next_step": ROUTING[referral]}
    await ctx.store.set("state", state)
    case = await ctx.store.get("case")
    R.log_audit(case, "InvestigationDecision", f"referral {referral}", rationale)
    await ctx.store.set("case", case)
    return f"{referral} → {ROUTING[referral]}"

ARGUE = ("First call get_case_file once. Then call submit_argument once with your structured "
         "argument, citing specific evidence and listing the weaknesses of your OWN argument.")

fraud_advocate = FunctionAgent(
    name="FraudAdvocate", description="Argues the case for fraud.",
    system_prompt=("You are an insurance fraud investigator. Build the strongest possible case "
                   "that this claim is fraudulent. " + ARGUE + " Then hand off to LegitimacyAdvocate."),
    llm=llm, tools=[get_case_file, submit_argument], can_handoff_to=["LegitimacyAdvocate"])

legitimacy_advocate = FunctionAgent(
    name="LegitimacyAdvocate", description="Argues the claim is legitimate.",
    system_prompt=("You are a consumer-protection advocate. Build the strongest possible case "
                   "that this claim is legitimate; give an innocent explanation for EVERY red "
                   "flag. " + ARGUE + " Then hand off to InvestigationDecision."),
    llm=llm, tools=[get_case_file, submit_argument], can_handoff_to=["InvestigationDecision"])

investigation_decision = FunctionAgent(
    name="InvestigationDecision", description="Weighs both arguments.",
    system_prompt=("You are the senior fraud investigator. Weigh both arguments above on evidence "
                   "quality, not on confidence alone. Call produce_fraud_determination once with "
                   "a referral: strong_fraud_indicators, likely_fraud, inconclusive or "
                   "likely_legitimate. You never declare fraud: that is a legal conclusion."),
    llm=llm, tools=[produce_fraud_determination], can_handoff_to=[])

async def investigate(claim_state: dict) -> dict:
    """claim_state: the pipeline's final state (claim + audit_log) for an ESCALATED claim."""
    workflow = AgentWorkflow(
        agents=[fraud_advocate, legitimacy_advocate, investigation_decision],
        root_agent="FraudAdvocate",
        initial_state={"arguments": {}, "determination": None},
    )
    ctx = Context(workflow)
    await ctx.store.set("case", claim_state)           # claim + audit log: kept out of "state"
    handler = workflow.run(user_msg="Investigate the escalated claim.", ctx=ctx, max_iterations=40)
    last = None
    async for ev in handler.stream_events():
        if isinstance(ev, AgentStream) and ev.current_agent_name != last:
            last = ev.current_agent_name
            print(f"\n== {last} " + "=" * (40 - len(last)))
        if isinstance(ev, AgentStream) and ev.delta:
            print(ev.delta, end="", flush=True)
    await handler
    state, case = await ctx.store.get("state"), await ctx.store.get("case")
    return {**state, "audit_log": case["audit_log"]}


if __name__ == "__main__":
    escalated = R.run_offline(R.sample_state(suspicious=True))   # stage 1: pipeline rules
    print("Pipeline decision:", escalated["claim"]["decision"], "→ starting the investigation")
    result = asyncio.run(investigate(escalated))
    for side, arg in result["arguments"].items():
        print(f"\n{side.upper():10} confidence {arg['confidence']:.2f} · weaknesses: {arg['weaknesses']}")
    d = result["determination"]
    print(f"\nREFERRAL: {d['referral']} → {d['next_step']}\nWhy: {d['rationale']}")
