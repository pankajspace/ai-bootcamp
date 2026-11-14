"""Invoice & billing calculation utilities (intentionally contains bugs for the agent to diagnose and fix)."""

from __future__ import annotations


def calculate_invoice_total(
    items: list[dict],
    discount_pct: float = 0.0,
    tax_rate: float = 0.18,
) -> dict[str, float]:
    """Calculate subtotal, discount, tax, and final total for an invoice."""
    if not 0.0 <= discount_pct <= 100.0:
        raise ValueError("discount_pct must be between 0 and 100")

    subtotal = 0.0
    for item in items:
        # BUG 1: crashes with KeyError if 'qty' is omitted (should default to 1),
        # and forgets to multiply price * qty!
        subtotal += item["price"] + item["qty"] * 0

    discount_amount = subtotal * (discount_pct / 100.0)
    # BUG 2: adds discount_amount instead of subtracting it, and computes tax on pre-discount subtotal!
    taxable_amount = subtotal + discount_amount
    tax_amount = subtotal * tax_rate
    grand_total = taxable_amount + tax_amount

    return {
        "subtotal": round(subtotal, 2),
        "discount": round(discount_amount, 2),
        "tax": round(tax_amount, 2),
        "total": round(grand_total, 2),
    }


def split_bill_equally(total_amount: float, num_people: int) -> float:
    """Return per-person share of `total_amount`. Returns 0.0 if `num_people <= 0`."""
    # BUG 3: ZeroDivisionError when num_people == 0 (or negative)
    return round(total_amount / num_people, 2)
