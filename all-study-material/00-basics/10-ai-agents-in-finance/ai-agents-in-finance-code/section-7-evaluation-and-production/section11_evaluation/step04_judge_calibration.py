"""
Section 11 lab — Can we trust the LLM judge? Calibrate it against humans
=======================================================================
An LLM judge is a model too. Before its "grounded / ungrounded" labels count
as evidence, compare them with labels from human reviewers on the same cases.

Raw agreement is misleading: if 80% of answers are grounded, a lazy judge that
always says "grounded" agrees 80% of the time while knowing nothing. Cohen's
kappa removes the agreement you'd get by chance:

    kappa = (observed agreement − chance agreement) / (1 − chance agreement)

A common bar: kappa ≥ 0.70 on 50–100 human-labelled cases before you trust the judge.

How to run
----------
No installs, no API key:   python step04_judge_calibration.py
"""

from __future__ import annotations

import random


def cohen_kappa(a: list[str], b: list[str]) -> float:
    n = len(a)
    labels = set(a) | set(b)
    observed = sum(x == y for x, y in zip(a, b)) / n
    chance = sum((a.count(lab) / n) * (b.count(lab) / n) for lab in labels)
    return 1.0 if chance == 1 else (observed - chance) / (1 - chance)


def bootstrap_ci(a: list[str], b: list[str], n_boot: int = 2000, seed: int = 0) -> tuple[float, float]:
    """Resample the cases with replacement many times; the middle 95% of kappas is the CI."""
    rng = random.Random(seed)
    n, values = len(a), []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        values.append(cohen_kappa([a[i] for i in idx], [b[i] for i in idx]))
    values.sort()
    return values[int(0.025 * n_boot)], values[int(0.975 * n_boot) - 1]

def make_cases(n: int = 60, seed: int = 1):
    """Human labels plus answer length (long answers tempt a 'verbosity-biased' judge)."""
    rng = random.Random(seed)
    human = ["grounded" if rng.random() < 0.8 else "ungrounded" for _ in range(n)]
    # padded, made-up answers tend to run long: that's what a biased judge latches onto
    words = [rng.randint(40, 200) if h == "grounded" else rng.randint(130, 260) for h in human]
    return human, words


def careful_judge(human, words, seed=2):
    rng = random.Random(seed)                # agrees with people ~93% of the time
    flip = {"grounded": "ungrounded", "ungrounded": "grounded"}
    return [flip[h] if rng.random() < 0.07 else h for h in human]


def verbose_judge(human, words):
    return ["grounded" if w > 150 else h for h, w in zip(human, words)]   # long = "must be good"


def lazy_judge(human, words):
    return ["grounded"] * len(human)         # never thinks


if __name__ == "__main__":
    human, words = make_cases()
    print(f"{len(human)} cases labelled by compliance reviewers "
          f"({human.count('grounded')} grounded, {human.count('ungrounded')} ungrounded)\n")
    print(f"{'judge':<16}{'agreement':>10}{'kappa':>8}{'95% CI':>16}   verdict")
    for name, judge in (("careful", careful_judge), ("verbosity-biased", verbose_judge), ("always 'yes'", lazy_judge)):
        labels = judge(human, words)
        agree = sum(x == y for x, y in zip(human, labels)) / len(human)
        k = cohen_kappa(human, labels)
        lo, hi = bootstrap_ci(human, labels)
        verdict = "use it" if lo >= 0.70 else "promising, label more cases" if k >= 0.70 else "do NOT use"
        print(f"{name:<16}{agree:>10.0%}{k:>8.2f}{f'{lo:.2f}–{hi:.2f}':>16}   {verdict}")
    print("\nWith ~60 cases the kappa CI is wide (often ±0.1–0.2): the 'careful' judge clears 0.70")
    print("but can't yet prove it with confidence. Label more cases before relying on it.")
