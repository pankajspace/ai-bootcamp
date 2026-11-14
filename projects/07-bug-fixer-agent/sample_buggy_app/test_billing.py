"""Unit tests for sample_buggy_app/billing.py."""

import unittest

from billing import calculate_invoice_total, split_bill_equally


class TestBilling(unittest.TestCase):
    def test_invoice_with_quantities_and_discount(self):
        items = [
            {"name": "Keyboard", "price": 1000.0, "qty": 2},
            {"name": "Mouse", "price": 500.0, "qty": 1},
        ]
        # Subtotal = 2500.0, 10% discount = 250.0, taxable = 2250.0, 18% tax = 405.0, total = 2655.0
        result = calculate_invoice_total(items, discount_pct=10.0, tax_rate=0.18)
        self.assertEqual(result["subtotal"], 2500.0)
        self.assertEqual(result["discount"], 250.0)
        self.assertEqual(result["tax"], 405.0)
        self.assertEqual(result["total"], 2655.0)

    def test_invoice_defaults_missing_qty_to_one(self):
        items = [{"name": "Monitor", "price": 10000.0}]
        result = calculate_invoice_total(items, discount_pct=0.0, tax_rate=0.18)
        self.assertEqual(result["subtotal"], 10000.0)
        self.assertEqual(result["total"], 11800.0)

    def test_split_bill_equally_handles_zero_and_negative_people(self):
        self.assertEqual(split_bill_equally(1200.0, 4), 300.0)
        self.assertEqual(split_bill_equally(1200.0, 0), 0.0)
        self.assertEqual(split_bill_equally(1200.0, -2), 0.0)


if __name__ == "__main__":
    unittest.main()
