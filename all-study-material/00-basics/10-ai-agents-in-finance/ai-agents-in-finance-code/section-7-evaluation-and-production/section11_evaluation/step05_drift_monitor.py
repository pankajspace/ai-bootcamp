"""
Section 11 lab — Has production traffic drifted away from what we validated?
===========================================================================
An evaluation is a snapshot. If next month's applicants look different, last
month's scorecard no longer describes the system. Three classic tests compare
a BASELINE sample with a CURRENT sample:

    PSI            how much the share of cases in each bucket moved     < 0.10 stable · 0.10–0.25 watch · > 0.25 act
    KS test        biggest gap between the two cumulative curves        p-value: could chance explain it?
    Mann-Whitney   does one sample tend to have larger values?          p-value, robust to outliers

How to run
----------
No installs, no API key. Keep it next to step01_kyc_agent.py and step02_kyc_dataset.py:
    python step05_drift_monitor.py
"""

from __future__ import annotations

import math
import random


def psi(baseline: list[float], current: list[float], edges: list[float]) -> float:
    """Population Stability Index over fixed buckets: Σ (cur% − base%) × ln(cur% / base%)."""
    def shares(xs):
        counts = [0] * (len(edges) + 1)
        for x in xs:
            counts[sum(x >= e for e in edges)] += 1          # bucket index = edges passed
        return [max(c / len(xs), 1e-4) for c in counts]       # avoid log(0)
    b, c = shares(baseline), shares(current)
    return sum((ci - bi) * math.log(ci / bi) for bi, ci in zip(b, c))


def psi_noise_floor(n: int, m: int, n_buckets: int) -> float:
    """Average PSI you'd see from sampling noise alone, with NO real drift."""
    return (1 / n + 1 / m) * (n_buckets - 1)

def ks_2samp(a: list[float], b: list[float]) -> tuple[float, float]:
    """Two-sample Kolmogorov–Smirnov: D = largest gap between the two cumulative curves."""
    a, b = sorted(a), sorted(b)
    i = j = 0
    d = 0.0
    while i < len(a) and j < len(b):
        x = min(a[i], b[j])
        while i < len(a) and a[i] == x:
            i += 1
        while j < len(b) and b[j] == x:
            j += 1
        d = max(d, abs(i / len(a) - j / len(b)))
    en = math.sqrt(len(a) * len(b) / (len(a) + len(b)))
    lam = (en + 0.12 + 0.11 / en) * d
    p = 2 * sum((-1) ** (k - 1) * math.exp(-2 * k * k * lam * lam) for k in range(1, 101))
    return d, min(1.0, max(0.0, p))


def mann_whitney(a: list[float], b: list[float]) -> tuple[float, float]:
    """Rank everything together; if one sample's ranks are systematically higher, it shifted.

    No tie correction, so with many tied values the p-value is slightly conservative.
    """
    pooled = sorted((v, g) for g, xs in ((0, a), (1, b)) for v in xs)
    ranks, k = [0.0] * len(pooled), 0
    while k < len(pooled):                                      # average ranks for ties
        end = k
        while end + 1 < len(pooled) and pooled[end + 1][0] == pooled[k][0]:
            end += 1
        for t in range(k, end + 1):
            ranks[t] = (k + end) / 2 + 1
        k = end + 1
    r_a = sum(r for r, (_, g) in zip(ranks, pooled) if g == 0)
    n1, n2 = len(a), len(b)
    u = r_a - n1 * (n1 + 1) / 2
    z = (u - n1 * n2 / 2) / math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    return u, math.erfc(abs(z) / math.sqrt(2))

def level(value: float) -> str:
    return "stable" if value < 0.10 else "WATCH" if value < 0.25 else "ACT"


if __name__ == "__main__":
    from step01_kyc_agent import risk_points
    from step02_kyc_dataset import _applicant

    def month(seed: int, share_high_risk_country: float, n: int = 500):
        rng = random.Random(seed)
        apps = [_applicant(rng, f"M{seed}-{i}") for i in range(n)]
        for a in apps:
            a.country = "XR" if rng.random() < share_high_risk_country else rng.choice(["GB", "DE", "US", "FR", "IN", "SG"])
        latency = [rng.lognormvariate(2.7, 0.35) for _ in range(n)]     # seconds per decision
        return [risk_points(a) for a in apps], latency

    edges = [20, 35, 50, 70, 90]                       # risk-point buckets around the tier lines
    base_pts, base_lat = month(1, 0.10)
    scenarios = {"next month, same mix": month(2, 0.10),
                 "new partner sends XR clients": month(3, 0.35),
                 "XR becomes the main market": month(4, 0.60)}
    floor = psi_noise_floor(500, 500, len(edges) + 1)
    print(f"Noise floor: with 500 vs 500 cases and {len(edges) + 1} buckets, PSI ≈ {floor:.3f} even with no drift.\n")
    print(f"{'scenario':<30}{'PSI':>7}  {'level':<7}{'KS D':>7}{'KS p':>9}{'MW p':>9}")
    for name, (pts, lat) in scenarios.items():
        value = psi(base_pts, pts, edges)
        d, p_ks = ks_2samp(base_pts, pts)
        _, p_mw = mann_whitney(base_pts, pts)
        print(f"{name:<30}{value:>7.3f}  {level(value):<7}{d:>7.3f}{p_ks:>9.4f}{p_mw:>9.4f}")
    d, p_ks = ks_2samp(base_lat, scenarios["next month, same mix"][1])
    print(f"\nLatency, same mix: KS D = {d:.3f}, p = {p_ks:.2f}  → no evidence of drift")
