"""
step01_self_refine.py — Monday at Future with Shivank Bank: draft an investment
thesis, then let the SAME model critique it and polish it.

    generate  →  feedback  →  refine  →  feedback  →  refine …  (max 3 rounds)

Run it:
    pip install anthropic python-dotenv
    # put ANTHROPIC_API_KEY=sk-ant-... in a .env file next to this script
    python step01_self_refine.py
"""
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()                                   # copies .env into os.environ
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
MODEL = "claude-sonnet-4-6"                     # any current Claude model works
MAX_ITERATIONS = 3                              # at most 3 feedback → refine rounds


def call_llm(prompt: str, max_tokens: int = 1024) -> str:
    """One plain LLM call. All three roles below use THIS same function."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text             # the reply's text


def generate_initial_thesis(financials: str) -> str:
    """Role 1 — the analyst writes a first draft."""
    prompt = f"""You are a senior equity analyst at a long-only asset management firm.
Draft a concise investment thesis based on the following financial data:

{financials}

Your thesis should cover: key business drivers, valuation, and 2-3 key risks.
Cite only metrics present in the data above; flag any outside claim as [unverified].
Write 1-2 sentences for each section. Be concise."""
    return call_llm(prompt)


def get_feedback(thesis: str, financials: str, history_feedback: str) -> str:
    """Role 2 — the investment committee reviews the draft."""
    prompt = f"""You are a critical investment committee reviewer.
Review the following investment thesis and provide specific, actionable feedback.
Identify missing information, weak arguments, or factual gaps.
Ground your feedback only on the metrics present in the provided data
[Original query]; flag any outside claim as [unverified].
Your feedback should cover the thesis sections: key business drivers,
valuation, and 2-3 key risks.
If no issue would block investment-committee approval, respond with exactly:
NO_FURTHER_FEEDBACK
Be concise.

Original query:
{financials}

Previous theses and feedback:
{history_feedback}

Thesis to provide feedback on:
{thesis}

Feedback:"""
    return call_llm(prompt)


def refine_thesis(thesis: str, feedback: str, financials: str,
                  history_feedback: str) -> str:
    """Role 3 — the analyst rewrites the draft to answer every comment."""
    prompt = f"""You are a senior equity analyst.
Revise the following investment thesis based on the reviewer feedback below.
Produce an improved version that directly addresses each point in the feedback.
Cite only metrics present in the provided data [Original query]; flag any
outside claim as [unverified].
Keep the same sections as the original: key business drivers, valuation,
and 2-3 key risks. Write 1-2 sentences for each section. Be concise.

Original query:
{financials}

Previous theses and feedback:
{history_feedback}

Original thesis to revise:
{thesis}

Reviewer feedback:
{feedback}

Revised thesis:"""
    return call_llm(prompt, max_tokens=2048)


def self_refine_thesis(financials: str) -> tuple[str, str]:
    print("[STEP 1] Generating initial thesis ...")
    thesis = generate_initial_thesis(financials)              # ① draft v0
    history_feedback = ""                                     # ② empty audit log
    print(f"Initial thesis:\n{thesis}\n")

    for iteration in range(1, MAX_ITERATIONS + 1):            # ③ 1, 2, 3
        print(f"[STEP 2] Iteration {iteration} -- getting feedback ...")
        feedback = get_feedback(thesis, financials, history_feedback)
        print(f"Feedback:\n{feedback}\n")
        if feedback.strip().startswith("NO_FURTHER_FEEDBACK"):  # ④ early stop
            print("Stopping: the reviewer has no blocking issues left.")
            break
        history_feedback += (                                  # ⑤ remember this round
            f"Iteration: {iteration}\nThesis: {thesis}\nFeedback: {feedback}\n\n"
        )
        print(f"[STEP 3] Iteration {iteration} -- refining thesis ...")
        thesis = refine_thesis(thesis, feedback, financials,   # ⑥ overwrite with v+1
                               history_feedback)
        print(f"Refined thesis:\n{thesis}\n")

    return thesis, history_feedback                           # ⑦ best draft + audit log


FINANCIALS = """
----- AAPL -----
Revenue FY2023: $383B (+2% YoY)
Services Revenue: $78B (+16% YoY), Gross Margin ~70%
Net Income: $97B
P/E (forward): 28x | EV/EBITDA: 22x
Cash & Equivalents: $62B | Net Debt: -$52B (net cash)
"""

if __name__ == "__main__":
    # Note: the prompt grows a little every round, because history_feedback grows.
    final_thesis, audit_log = self_refine_thesis(FINANCIALS)
    print("FINAL THESIS:\n", final_thesis)
