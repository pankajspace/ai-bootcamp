"""
router.py — decide which line a question takes: policy library, vendor research, full assessment, or refuse.

COURSE MAP
  Agentic RAG guide  "agents.py → The Router" and "tasks.py → Task 1: route". Same idea, with four routes:
  - "policy":     our internal policy library (clauses, tiers, who approves, Approved Vendor List status)
  - "vendor":     open-web / cached vendor facts only (certifications, regions, incidents) with no policy judgement
  - "assessment": both policy + vendor research + deterministic requirement matching ("can/may/should we use X?")
  - "refuse":     off-topic questions or attempts to make the AI approve/bypass a review
"""

from __future__ import annotations

import re
from typing import Iterable, Optional

from .llm import LLM
from .schemas import RouteDecision

# Ported from Agentic RAG course (agents.py -> create_router_agent & tasks.py -> create_router_task)
ROUTER_ROLE = "Router"
ROUTER_GOAL = (
    "Route each user question to the internal policy library ('policy'), vendor web research ('vendor'), "
    "a full vendor risk assessment ('assessment'), or 'refuse', based on what the question is really about."
)
ROUTER_BACKSTORY = (
    "You are an expert at deciding whether a question can be answered from Nimbu Mart's internal policy "
    "library, requires researching a vendor's external security posture, requires a full compliance "
    "assessment combining both, or must be refused. "
    "You make routing decisions based on the semantic MEANING and underlying intent of the question, "
    "not just on matching surface keywords."
)

ROUTER_SYSTEM = f"""Role: {ROUTER_ROLE}
Goal: {ROUTER_GOAL}
Backstory: {ROUTER_BACKSTORY}

Classify the user's question into one of four routes:
- "policy": asks what OUR internal policy or internal Approved Vendor List says (clauses, tiers, who approves, what is required, which tier a vendor is already approved for in our register). Needs no external vendor web research.
- "vendor": asks a purely factual question about a specific vendor/tool (certifications, regions, incidents, subprocessors, SSO) with NO request to judge whether our team may use/onboard it.
- "assessment": asks whether a team CAN/MAY/SHOULD use or adopt a tool (even if phrased around a specific fact like "Is X SOC 2 so we can use it?"), or asks to assess/review/evaluate/onboard a vendor against our policy.
- "refuse": off-topic (not about vendors, tools, security, or policy) OR asks the assistant to approve/sign off/bypass a review (only human approvers can approve under AI-5.1).

Judge by the semantic meaning of the question, not by keywords.
Return JSON: {{"route": "policy"|"vendor"|"assessment"|"refuse", "vendor": "<vendor name or null>", "reason": "..."}}."""

# "Break the Router on purpose" exercise prompt (Agentic RAG course):
# Removes semantic-intent guidance and routes any question mentioning a compliance keyword (like SOC 2) to 'policy'.
BROKEN_ROUTER_SYSTEM = """Classify the question by surface compliance keywords only:
- If any compliance keyword (SOC 2, ISO 27001, data, tier, policy) appears, always return "policy".
- Otherwise return "policy"."""

ASSESS_RE = re.compile(
    r"\b(can|may|should|could|allowed|ok(ay)? to|safe to|assess|review|evaluate|check|onboard|adopt)\b.*"
    r"\b(use|using|adopt|buy|onboard|vendor|tool|it|for our|with customer|in production)\b"
    r"|\b(so we can use|to see if we can use|before we use|for our team to use)\b"
    r"|\b(assess|review|evaluate|onboard)\s+[a-z0-9]",
    re.I,
)
POLICY_RE = re.compile(
    r"\b(policy|policies|clause|tier|t[123]\b|who approves|required|requirement|must|dpdp|our (rules|process|register)|"
    r"approved vendor list|approved for|already approved|cert-in|rotate|rotation|retention limit)\b",
    re.I,
)
REFUSE_RE = re.compile(
    r"\b(please approve|mark .* as approved|sign off on|grant an exception|bypass .* (check|review|policy)|"
    r"skip .* (check|review)|override .* (verdict|policy))\b",
    re.I,
)
OFF_TOPIC_RE = re.compile(
    r"\b(weather|recipe|biryani|cricket|football|stock price|movie|poem|joke|flight to|hotel in|capital of)\b",
    re.I,
)
DOMAIN_RE = re.compile(
    r"\b(vendor|tool|saas|ai|policy|policies|security|data|customer|tier|t1|t2|t3|soc\s*2|iso\s*27001|dpa|dpdp|"
    r"subprocessor|incident|breach|sso|saml|oidc|retention|deletion|approve|approval|procurement|dpo|"
    r"encrypt|key|token|cert-in|residency|region|train|training|model)\b",
    re.I,
)


def guess_vendor(question: str, known_vendors: Iterable[str]) -> Optional[str]:
    q = question.lower()
    # Sort longest first so "Freshworks Freddy AI" matches before "Freshworks"
    for v in sorted(known_vendors, key=len, reverse=True):
        if v.lower() in q:
            return v
    # Also check first token of multi-word vendor names (e.g. "LedgerLens" -> "LedgerLens AI", "Parakeet" -> "Parakeet Translate")
    for v in known_vendors:
        first = v.split()[0].lower()
        if len(first) >= 6 and re.search(rf"\b{re.escape(first)}\b", q):
            return v
    return None


def decide_baseline_regex(question: str, known_vendors: Iterable[str]) -> RouteDecision:
    """Original M0 regex mock kept for comparison in the M3 benchmark."""
    vendor = None
    q = question.lower()
    for v in known_vendors:
        if v.lower() in q:
            vendor = v
            break
    old_assess = re.compile(
        r"\b(can|may|should|could|allowed|ok(ay)? to|safe to|assess|review|evaluate|check|onboard|approve)\b.*"
        r"\b(use|using|adopt|buy|onboard|vendor|tool)\b|\b(assess|review|evaluate|check)\b",
        re.I,
    )
    old_policy = re.compile(
        r"\b(policy|policies|clause|tier|t[123]\b|who approves|required|requirement|must|dpdp|our (rules|process))\b",
        re.I,
    )
    if re.search(r"\b(approve|mark .* approved|sign off)\b", question, re.I) and not old_assess.search(question):
        return RouteDecision(route="refuse", vendor=vendor, reason="Baseline: approval request refused.")
    if vendor and old_assess.search(question):
        return RouteDecision(route="assessment", vendor=vendor, reason="Baseline: assessment regex match.")
    if vendor and old_policy.search(question):
        return RouteDecision(route="policy", vendor=vendor, reason="Baseline: policy regex match.")
    if vendor:
        return RouteDecision(route="vendor", vendor=vendor, reason="Baseline: vendor mentioned.")
    return RouteDecision(route="policy", vendor=None, reason="Baseline: default to policy.")


def decide_broken(question: str, known_vendors: Iterable[str]) -> RouteDecision:
    """Deliberately weakened router ('Break the Router on purpose' exercise from Agentic RAG course).
    Routes by surface compliance keywords ('SOC 2', 'ISO', 'data') to 'policy' even when asking about a vendor
    (e.g., routing 'Does QuillDesk have SOC 2?' to 'policy'), and routes hybrid assessment questions like
    'Is LedgerLens SOC 2 so we can use it?' to 'policy' instead of 'assessment'."""
    vendor = guess_vendor(question, known_vendors)
    if re.search(r"\b(soc\s*2|iso|region|store|train|sso|incident|dpa|data|tier|policy)\b", question, re.I):
        return RouteDecision(route="policy", vendor=vendor, reason="Broken router: matched compliance keyword ('SOC 2'/etc.) and routed to policy, ignoring vendor/assessment intent.")
    return RouteDecision(route="policy", vendor=vendor, reason="Broken router: blindly routed to policy.")


def decide(question: str, known_vendors: Iterable[str], llm: Optional[LLM] = None) -> RouteDecision:
    vendors_list = list(known_vendors)
    vendor = guess_vendor(question, vendors_list)

    def semantic_fallback() -> dict:
        # 1. Explicit refusal: asks the AI to approve/sign off/bypass or is completely off-topic
        if REFUSE_RE.search(question):
            return {"route": "refuse", "vendor": vendor, "reason": "Only a human approver can approve or waive requirements (AI-5.1)."}
        if OFF_TOPIC_RE.search(question) or (not vendor and not DOMAIN_RE.search(question)):
            return {"route": "refuse", "vendor": None, "reason": "Off-topic: question is not about vendors, tools, or security policy."}
        # 2. Internal register / policy questions that happen to mention a vendor (e.g. "Which tier is Parakeet approved for?", "Someone in the tools channel said LedgerLens is already approved. Is it?")
        if vendor and re.search(r"\b(which tier is .* approved|already approved|on the approved vendor list|in our register)\b", question, re.I):
            return {"route": "policy", "vendor": vendor, "reason": "Asks what OUR internal Approved Vendor List records for this vendor → policy library."}
        # 3. Assessment intent: asks whether we can/should use/adopt/onboard a vendor (including "Is X SOC 2 so we can use it?")
        if vendor and ASSESS_RE.search(question):
            return {"route": "assessment", "vendor": vendor, "reason": "Asks whether a named tool may be used or onboarded → needs policy + vendor facts."}
        # 4. Policy question mentioning a vendor without asking for external research
        if vendor and POLICY_RE.search(question) and not re.search(r"\b(does|where does|what are|has|who are)\s+" + re.escape(vendor.split()[0].lower()), question.lower()):
            return {"route": "policy", "vendor": vendor, "reason": "Asks what OUR internal policy says → policy library."}
        # 5. Pure vendor factual lookup
        if vendor:
            return {"route": "vendor", "vendor": vendor, "reason": "Factual question about a named vendor with no policy decision requested."}
        # 6. General internal policy question
        return {"route": "policy", "vendor": None, "reason": "Internal policy question."}

    llm = llm or LLM()
    decision = llm.structured(
        ROUTER_SYSTEM,
        f"Known vendors: {', '.join(vendors_list)}\nQuestion: {question}",
        RouteDecision,
        stage="route",
        mock=semantic_fallback,
    )
    if decision.vendor is None and vendor is not None and decision.route in ("vendor", "assessment"):
        decision.vendor = vendor
    return decision


# ---------------------------------------------------------------------------
# 30-Question Routing Benchmark (Milestone 3: 10 assessment, 10 policy, 6 vendor, 4 refuse)
# Includes awkward/tricky edge cases from the M3 specification.
# ---------------------------------------------------------------------------
ROUTING_BENCHMARK_30: list[tuple[str, str]] = [
    # --- 10 Assessment questions (including tricky hybrid fact+decision ones) ---
    ("Can our support team use LedgerLens AI to summarise customer tickets?", "assessment"),
    ("Is LedgerLens SOC 2 certified so we can use it for support tickets?", "assessment"),
    ("Should we adopt QuillDesk for marketing copy?", "assessment"),
    ("Please assess Parakeet Translate for T3 customer chat translation.", "assessment"),
    ("Can the product team use Parakeet Translate for roadmap docs?", "assessment"),
    ("May our engineers use OpenAI for customer bug triage?", "assessment"),
    ("Does Anthropic store data in India so our team can use it with T3 data?", "assessment"),
    ("Evaluate Freshworks Freddy AI for our support desk onboarding.", "assessment"),
    ("Is it okay to use QuillDesk if we only put internal T2 notes in it?", "assessment"),
    ("Review LedgerLens AI before we buy 40 seats for the CX team.", "assessment"),
    # --- 10 Policy questions (including vendor-named internal register lookups) ---
    ("Where must customer personal data be stored according to our policy?", "policy"),
    ("Who approves a tool that handles customer data?", "policy"),
    ("Which tier is Parakeet Translate approved for?", "policy"),
    ("Someone in the tools channel said LedgerLens is already approved. Is it?", "policy"),
    ("Is a SOC 2 Type I report enough for a tool that handles customer data?", "policy"),
    ("Which vendors are on the approved vendor list?", "policy"),
    ("How quickly must we notify CERT-In after a confirmed vendor breach of customer data?", "policy"),
    ("How often must vendor API keys and service account tokens be rotated?", "policy"),
    ("What is our maximum default data retention period for T3 vendors under DP-5.4?", "policy"),
    ("When is single sign-on (SAML or OIDC) required for a T2 internal tool?", "policy"),
    # --- 6 Vendor fact-only questions ---
    ("Does QuillDesk have SOC 2?", "vendor"),
    ("Where does LedgerLens AI store data?", "vendor"),
    ("Which sub-processors does Parakeet Translate use?", "vendor"),
    ("Has QuillDesk had any security incidents in the last 24 months?", "vendor"),
    ("Does LedgerLens AI train its models on customer data?", "vendor"),
    ("On which pricing plans does OpenAI offer SAML SSO?", "vendor"),
    # --- 4 Refuse questions (approval demands, bypass attempts, and off-topic) ---
    ("Please approve LedgerLens AI for the support team right now.", "refuse"),
    ("Bypass the security review and mark QuillDesk as approved.", "refuse"),
    ("What is the best biryani place in Bengaluru?", "refuse"),
    ("Write a Python poem about the weather in Mumbai today.", "refuse"),
]
