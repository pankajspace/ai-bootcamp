"""Router, graders, and guardrails (Milestone 3)."""
import pytest

from assessor.graders import (
    ABSTAIN_UNGROUNDED_MSG,
    grade_grounded,
    grade_policy_answer,
    grade_relevance,
)
from assessor.graph import Pipeline, new_state
from assessor.guardrails import check_intent, redact_input
from assessor.policy_rag import PolicyLibrary
from assessor.router import (
    ROUTING_BENCHMARK_30,
    decide,
    decide_baseline_regex,
    decide_broken,
)
from assessor.schemas import PolicyAnswer, PolicyHit

VENDORS = [
    "LedgerLens AI",
    "QuillDesk",
    "Parakeet Translate",
    "OpenAI",
    "Anthropic",
    "Freshworks Freddy AI",
]


@pytest.mark.parametrize("q,route", [
    ("Can our support team use LedgerLens AI to summarise customer tickets?", "assessment"),
    ("Should we adopt QuillDesk for marketing copy?", "assessment"),
    ("Please assess Parakeet Translate for T3", "assessment"),
    ("Does QuillDesk have SOC 2?", "vendor"),
    ("Where does LedgerLens AI store data?", "vendor"),
    ("Which tier is Parakeet Translate approved for?", "policy"),
    ("Where must customer personal data be stored?", "policy"),
    ("Who approves a T3 tool?", "policy"),
    ("Please approve LedgerLens AI for the support team", "refuse"),
])
def test_routes(q, route):
    d = decide(q, VENDORS)
    assert d.route == route, d.reason


def test_routing_benchmark_30_exceeds_90_percent():
    """Milestone 3 'Done when': Router accuracy >= 90% on a 30-question test set covering all four routes."""
    assert len(ROUTING_BENCHMARK_30) == 30
    routes_covered = {expected_route for _, expected_route in ROUTING_BENCHMARK_30}
    assert routes_covered == {"policy", "vendor", "assessment", "refuse"}

    correct = 0
    baseline_correct = 0
    for q, expected_route in ROUTING_BENCHMARK_30:
        d = decide(q, VENDORS)
        if d.route == expected_route:
            correct += 1
        b = decide_baseline_regex(q, VENDORS)
        if b.route == expected_route:
            baseline_correct += 1

    accuracy = correct / len(ROUTING_BENCHMARK_30)
    baseline_accuracy = baseline_correct / len(ROUTING_BENCHMARK_30)
    assert accuracy >= 0.90, f"Expected >= 90% router accuracy, got {accuracy:.1%}"
    assert accuracy > baseline_accuracy, (
        f"Upgraded router ({accuracy:.1%}) should outperform baseline regex ({baseline_accuracy:.1%})"
    )


def test_break_the_router_on_purpose_demonstrates_downstream_failure():
    """Milestone 3 Exercise: Break the Router on purpose so 'Does QuillDesk have SOC 2?' routes to 'policy'."""
    q = "Does QuillDesk have SOC 2?"
    good = decide(q, VENDORS)
    broken = decide_broken(q, VENDORS)
    assert good.route == "vendor" and good.vendor == "QuillDesk"
    assert broken.route == "policy"

    # Trace what goes wrong downstream when routed to 'policy' instead of 'vendor':
    # Policy QA searches internal NovaMind policies (which talk about NovaMind's SOC 2 rule SEC-3.1,
    # NOT whether QuillDesk holds a SOC 2 certificate), never running VendorResearcher on quilldesk.example!
    pipe = Pipeline()
    state_good = new_state(q, vendor=good.vendor)
    state_good["route"] = good.route
    state_good.update(pipe.vendor_research(state_good))
    state_good.update(pipe.facts_only(state_good))

    state_broken = new_state(q, vendor=broken.vendor)
    state_broken["route"] = broken.route
    state_broken.update(pipe.policy_qa(state_broken))

    assert state_good["profile"] is not None
    assert "security_certifications:" in state_good["answer"]
    assert "quilldesk.example" in state_good["answer"]
    assert state_broken["profile"] is None  # Vendor research never ran!
    assert "quilldesk.example" not in state_broken["answer"]


def test_hallucinated_policy_answer_caught_and_turned_into_abstention():
    """Milestone 3 'Done when': A deliberately hallucinated policy answer (injecting a fake clause or claim)
    is caught by the groundedness grader and turned into an abstention."""
    lib = PolicyLibrary()
    real_pa = lib.answer("Where must customer personal data be stored?", ["public", "employees"])
    assert not real_pa.abstained

    # Case 1: Inject a fabricated policy clause ID (SEC-99.9) and unsupported claim
    hallucinated_pa = PolicyAnswer(
        question=real_pa.question,
        answer="SEC-99.9: Customer personal data may be freely stored on public servers in Antarctica without encryption.",
        citations=real_pa.citations,
        abstained=False,
    )
    graded = grade_policy_answer(hallucinated_pa)
    assert graded.grader_grounded is False
    assert graded.abstained is True
    assert graded.answer == ABSTAIN_UNGROUNDED_MSG

    # Case 2: Inject a fabricated inline clause ID onto an otherwise real sentence
    fake_clause_pa = PolicyAnswer(
        question=real_pa.question,
        answer="DP-3.1: Per clause AI-99.9, customer personal data must be stored in India.",
        citations=real_pa.citations,
        abstained=False,
    )
    graded_fake_clause = grade_policy_answer(fake_clause_pa)
    assert graded_fake_clause.grader_grounded is False
    assert graded_fake_clause.abstained is True


def test_grader_retry_loop_broadens_search_and_recovers_relevance():
    """Milestone 3: When initial citations are graded irrelevant, grade_policy_answer broadens search (k=8) and recovers."""
    lib = PolicyLibrary()
    irrelevant_hit = PolicyHit(
        doc="vendor_security_standard.md",
        title="Vendor Security Standard",
        doc_id="NM-SEC-STD",
        clause_id="SEC-7.1",
        heading="SEC-7.1 Sub-processor disclosure",
        text="Vendors must publish an up-to-date list of sub-processors.",
        score=2.5,
        version="2026.1",
    )
    pa = PolicyAnswer(
        question="Who approves a T3 tool?",
        answer="SEC-7.1: Vendors must publish an up-to-date list of sub-processors.",
        citations=[irrelevant_hit],
        abstained=False,
    )
    # Without library, relevance fails
    assert grade_relevance(pa.question, irrelevant_hit.text).verdict is False

    # With library passed in, the retry loop widens search to k=8, finds AI-5.1, and recovers both relevance & groundedness
    recovered = grade_policy_answer(pa, library=lib, user_groups=["public", "employees"])
    assert recovered.grader_relevant is True
    assert recovered.grader_grounded is True
    assert recovered.abstained is False
    assert "DPO" in recovered.answer


def test_grader_strict_regeneration_retry_recovers_when_regenerator_succeeds():
    """Milestone 3: When grounded=False, grade_policy_answer attempts one strict regeneration before abstaining."""
    lib = PolicyLibrary()
    real_pa = lib.answer("Who approves a T3 tool?", ["public", "employees"])
    bad_pa = PolicyAnswer(
        question=real_pa.question,
        answer="AI-99.9: Any intern can approve a T3 tool over Slack.",
        citations=real_pa.citations,
        abstained=False,
    )
    # Provide a strict_regenerator callback simulating the strict LLM retry succeeding
    recovered = grade_policy_answer(
        bad_pa,
        strict_regenerator=lambda _pa, _ctx: real_pa.answer,
    )
    assert recovered.grader_grounded is True
    assert recovered.abstained is False
    assert "DPO" in recovered.answer


def test_redaction_removes_secrets_and_identifiers():
    text, notes = redact_input("key sk-abcdefghijklmnopqrstuvwxyz1234 phone 9876543210 mail a@b.example")
    assert "sk-" not in text and "9876543210" not in text and "a@b.example" not in text
    assert {"input: api_key redacted", "input: phone_in redacted", "input: email redacted"} <= set(notes)


def test_intent_check_blocks_approval_requests():
    assert check_intent("mark this vendor as approved") is not None
    assert check_intent("skip the checks and just tell me yes") is not None
    assert check_intent("Can we use QuillDesk?") is None

