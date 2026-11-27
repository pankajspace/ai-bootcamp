"""
step02_self_consistency.py — Tuesday: five independent "junior analysts" reason
about the same stock; the majority vote becomes the recommendation.

Run it:
    pip install anthropic python-dotenv
    python step02_self_consistency.py
"""
import os
from collections import Counter

import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
MODEL = "claude-sonnet-4-6"
N_PATHS = 5                 # how many independent analysts vote
TEMPERATURE = 0.8           # enough randomness for different reasoning paths

SYSTEM_PROMPT = """You are a financial analyst.
Analyze the stock summary of a company and provide a final recommendation:
BUY, HOLD, or SELL.
Reason step by step through the investment case. Cover:
1. Earnings quality and trajectory
2. Valuation vs. peers and history
3. Key risks and near-term catalysts
4. Overall risk/reward balance
Be concise: 1-2 sentences per point.
End your response with exactly one line in this plain format (no markdown,
no bold, no asterisks):
RECOMMENDATION: <BUY|HOLD|SELL>"""


def sample_reasoning_path(stock_summary: str) -> str:
    """One analyst = one ordinary API call."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": stock_summary}],
        # Anthropic SDK 1.0+ removed temperature from the method signature,
        # so we send it in extra_body. On SDK < 1.0 write temperature=TEMPERATURE.
        # If your model rejects temperature, delete this line: replies are
        # sampled (a bit random) anyway.
        extra_body={"temperature": TEMPERATURE},
    )
    return response.content[0].text


def extract_recommendation(path: str) -> str | None:
    """Find 'RECOMMENDATION: X' near the end, tolerating stray formatting."""
    for line in reversed(path.strip().split("\n")):           # ① last line first
        cleaned = line.strip().lstrip("*_`# ").upper()        # ② drop **, #, `, _
        if cleaned.startswith("RECOMMENDATION:"):             # ③ the contract line?
            label = cleaned.replace("RECOMMENDATION:", "").strip().strip("*_`. ")
            if label in ("BUY", "HOLD", "SELL"):              # ④ only legal labels
                return label
    return None                                               # ⑤ no valid line found


def self_consistency_recommend(stock_summary: str, n_paths: int = N_PATHS) -> dict:
    paths, recommendations = [], []
    print(f"[STEP 1] Sampling {n_paths} paths at temperature={TEMPERATURE}.\n")
    for i in range(1, n_paths + 1):
        print(f"[STEP 2] Sampling reasoning path {i}/{n_paths} ...")
        path = sample_reasoning_path(stock_summary)           # one analyst's notes
        recommendation = extract_recommendation(path)         # BUY / HOLD / SELL / None
        paths.append(path)
        recommendations.append(recommendation)
        print(f"--- Path {i} reasoning ---\n{path}\n")
        print(f"[Path {i}] Parsed recommendation: {recommendation}\n")

    print("[STEP 3] Aggregating answers via majority vote ...")
    valid = [r for r in recommendations if r is not None]     # drop unreadable paths
    if not valid:
        raise ValueError("No path ended with a valid RECOMMENDATION line.")
    vote_counts = Counter(valid)                              # {'HOLD': 3, 'SELL': 2}
    final_recommendation, top_votes = vote_counts.most_common(1)[0]
    agreement = top_votes / len(valid)                        # 3/5 = 0.6
    return {
        "final_recommendation": final_recommendation,
        "vote_counts": dict(vote_counts),
        "agreement": agreement,
        "needs_human_review": agreement < 0.8,                # a split vote = ambiguity
        "paths": paths,                                       # the audit trail
    }


STOCK_SUMMARY = """
Company: ACME Corp (ticker: ACME)
Latest Earnings:
- Revenue: $94.9B (+5% YoY), beat consensus by 1.2%
- EPS: $1.56, beat consensus by $0.04
- Net margin: 25.5% (down 80bps YoY)
- Free Cash Flow: $18.1B
Valuation:
- P/E: 28x (sector median: 22x)
- EV/EBITDA: 18x (sector median: 14x)
- PEG ratio: 1.9
Guidance:
- FY2025 revenue guidance raised to $97-99B
- Management flagged EU regulatory headwinds in H2
Market Context:
- Sector under pressure from rising rates
- Main competitor cut guidance last week
"""

if __name__ == "__main__":
    result = self_consistency_recommend(STOCK_SUMMARY)
    print(f"\n=== FINAL RECOMMENDATION: {result['final_recommendation']} ===")
    print(f"Vote breakdown: {result['vote_counts']}  "
          f"(agreement {result['agreement']:.0%})")
    if result["needs_human_review"]:
        print("Split vote -> send to a human analyst before acting.")
