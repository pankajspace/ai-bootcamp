"""
metric.py — the leaderboard score for "Vendor Verdict".

Kaggle-style entry point:  score(solution, submission, row_id_column_name) -> float   (higher is better)

Rows come in two kinds, told apart by the id suffix:
    <case_id>__<REQUIREMENT_ID>   verdict in PASS | FAIL | UNKNOWN | NEEDS_REVIEW
    <case_id>__OVERALL            verdict in BLOCKED | CONDITIONAL | READY_FOR_APPROVAL

    score = 0.60 * macro_F1(requirement verdicts)
          + 0.20 * accuracy(overall outcomes)
          + 0.20 * (1 - false_confidence_rate)

false_confidence_rate is the capstone's "guess rate": among requirement rows where the gold verdict is
UNKNOWN or NEEDS_REVIEW, the share where the submission said PASS or FAIL. Guessing is the dangerous
error in vendor review, so it has its own term; a model that refuses to commit still scores below one that
reads the evidence correctly, because macro-F1 is 60% of the score.

Only the standard library plus pandas/numpy is used, so it runs inside Kaggle's metric sandbox.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

REQ_LABELS = ("PASS", "FAIL", "UNKNOWN", "NEEDS_REVIEW")
OVERALL_LABELS = ("BLOCKED", "CONDITIONAL", "READY_FOR_APPROVAL")
W_F1, W_OVERALL, W_CONFIDENCE = 0.60, 0.20, 0.20


class ParticipantVisibleError(Exception):
    """Errors with this type are shown to the participant (bad format, wrong ids)."""


def _macro_f1(gold: np.ndarray, pred: np.ndarray) -> float:
    f1s = []
    for label in REQ_LABELS:
        tp = int(((gold == label) & (pred == label)).sum())
        fp = int(((gold != label) & (pred == label)).sum())
        fn = int(((gold == label) & (pred != label)).sum())
        if tp + fp + fn == 0:          # class absent from both: skip
            continue
        f1s.append(2 * tp / (2 * tp + fp + fn))
    return float(np.mean(f1s)) if f1s else 0.0


def components(solution: pd.DataFrame, submission: pd.DataFrame, row_id_column_name: str = "id") -> dict:
    if row_id_column_name not in submission.columns or "verdict" not in submission.columns:
        raise ParticipantVisibleError(f"Submission must have the columns '{row_id_column_name}' and 'verdict'.")
    if submission[row_id_column_name].duplicated().any():
        raise ParticipantVisibleError("Submission has duplicate ids.")
    sol = solution.drop(columns=[c for c in ("Usage", "usage", "split") if c in solution.columns]).copy()
    sub = submission[[row_id_column_name, "verdict"]].copy()
    sol[row_id_column_name] = sol[row_id_column_name].astype(str)
    sub[row_id_column_name] = sub[row_id_column_name].astype(str)
    if set(sub[row_id_column_name]) != set(sol[row_id_column_name]):
        missing = len(set(sol[row_id_column_name]) - set(sub[row_id_column_name]))
        extra = len(set(sub[row_id_column_name]) - set(sol[row_id_column_name]))
        raise ParticipantVisibleError(f"Submission ids do not match the test ids ({missing} missing, {extra} unexpected).")
    merged = sol.merge(sub, on=row_id_column_name, suffixes=("_gold", "_pred"))
    if merged["verdict_pred"].isna().any():
        raise ParticipantVisibleError("Submission has empty verdicts.")
    merged["verdict_pred"] = merged["verdict_pred"].astype(str).str.strip().str.upper()
    is_overall = merged[row_id_column_name].str.endswith("__OVERALL")

    req, ov = merged[~is_overall], merged[is_overall]
    bad_req = ~req["verdict_pred"].isin(REQ_LABELS)
    bad_ov = ~ov["verdict_pred"].isin(OVERALL_LABELS)
    if bad_req.any() or bad_ov.any():
        bad = pd.concat([req[bad_req], ov[bad_ov]])[row_id_column_name].head(3).tolist()
        raise ParticipantVisibleError(f"Invalid verdict labels, for example at ids {bad}. Requirement rows take {REQ_LABELS}; "
                                      f"__OVERALL rows take {OVERALL_LABELS}.")

    gold, pred = req["verdict_gold"].to_numpy(), req["verdict_pred"].to_numpy()
    uncertain = np.isin(gold, ("UNKNOWN", "NEEDS_REVIEW"))
    false_conf = float(np.isin(pred[uncertain], ("PASS", "FAIL")).mean()) if uncertain.any() else 0.0
    overall_acc = float((ov["verdict_gold"].to_numpy() == ov["verdict_pred"].to_numpy()).mean()) if len(ov) else 0.0
    f1 = _macro_f1(gold, pred)
    return {"macro_f1": f1, "overall_accuracy": overall_acc, "false_confidence_rate": false_conf,
            "score": W_F1 * f1 + W_OVERALL * overall_acc + W_CONFIDENCE * (1 - false_conf)}


def score(solution: pd.DataFrame, submission: pd.DataFrame, row_id_column_name: str = "id", **kwargs) -> float:
    return float(components(solution, submission, row_id_column_name)["score"])
