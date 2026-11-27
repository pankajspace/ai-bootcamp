"""
step04_critic_sketch.py — Thursday morning: fact-check the morning briefing.
A SIMPLIFIED SKETCH of the CRITIC loop (verify → critique → correct).
The "tools" and the "corrector" are stand-ins so you can run it offline:
    python step04_critic_sketch.py
"""
def verify(claims: dict, sources: dict, tolerance: float = 0.0005) -> list[str]:
    """Compare every number in the draft with the source (0.0005 = 0.05% slack)."""
    issues = []
    for field, source_value in sources.items():
        claimed = claims.get(field)
        if claimed is None:
            issues.append(f"{field}: missing from the draft (source says {source_value})")
        elif abs(claimed - source_value) > tolerance * abs(source_value):
            issues.append(f"{field}: draft says {claimed}, source says {source_value}")
    return issues                       # [] means "nothing wrong" → stop


def critic_loop(claims: dict, fetch_sources, correct, max_iters: int = 3):
    audit_trail = []
    for i in range(1, max_iters + 1):
        sources = fetch_sources()                     # VERIFY: ask the tools
        issues = verify(claims, sources)              # CRITIQUE: what's wrong?
        audit_trail.append({"round": i, "issues": issues})
        if not issues:                                # clean → done
            break
        claims = correct(claims, issues, sources)     # CORRECT: an LLM in real life
    return claims, audit_trail


if __name__ == "__main__":
    draft = {"open_price": 78.29, "ttm_revenue_bn": 45.0, "dividend_ps": 1.80}   # Coca-Cola

    def fetch_sources():          # stand-in for market-data / fundamentals / events APIs
        return {"open_price": 78.37, "ttm_revenue_bn": 46.0, "dividend_ps": 1.84}

    def correct(claims, issues, sources):   # stand-in for "LLM, fix these issues"
        return {**claims, **sources}

    final, trail = critic_loop(draft, fetch_sources, correct)
    for step in trail:
        print(step)
    print("Verified briefing numbers:", final)
