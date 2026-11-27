# validator.py — plain Python checks. No LLM anywhere in this file.
from common import CompanyMetrics, TaskStatus, ValidationResult


def validate_research(plan, results, required_tickers) -> ValidationResult:
    errors, warnings, gaps = [], [], []                  # ① three empty buckets

    # Check 1: did every task finish?
    for t in plan.sub_tasks:
        if t.status != TaskStatus.COMPLETED:
            gaps.append(f"Task {t.id} {t.status.value}: {t.description}")

    # Check 2: does every company appear somewhere in the findings?
    for ticker in required_tickers:
        if not any(ticker.upper() in r.upper() for r in results.values()):
            gaps.append(f"Missing data for {ticker}")

    # Check 3: are the numbers possible? are they plausible?
    for text in results.values():
        try:
            m = CompanyMetrics.model_validate_json(text)     # ② is it a metrics form?
        except ValueError:
            continue                                     #    news, filings… skip
        if m.gross_margin is not None and not -50 <= m.gross_margin <= 100:
            errors.append(f"{m.ticker}: gross margin {m.gross_margin}% is impossible")
        if (m.gross_margin is not None and m.operating_margin is not None
                and m.operating_margin > m.gross_margin):
            errors.append(f"{m.ticker}: operating margin is above gross margin")
        if m.pe_ratio is not None and not 0 < m.pe_ratio <= 150:
            warnings.append(f"{m.ticker}: P/E of {m.pe_ratio} is extreme"
                            " - check earnings")
        if m.revenue_growth is not None and abs(m.revenue_growth) > 300:
            warnings.append(f"{m.ticker}: revenue growth {m.revenue_growth}% - unit error?")

    return ValidationResult(                             # ③ the verdict
        is_valid=not errors and not gaps,
        errors=errors, warnings=warnings, gaps=gaps,
    )
