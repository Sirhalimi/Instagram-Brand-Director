"""Commercial catalog guard regression tests."""
import importlib.util
import unittest
from datetime import date
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "catalog_guard", Path(__file__).resolve().parents[1] / "scripts" / "catalog_guard.py"
)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.product = {
            "sku": "P-1", "name": "Example", "status": "active",
            "stock_policy": "tracked", "stock": 10,
            "price": "100", "unit_cost": "60", "currency": "USD",
            "fulfillment": "automatic", "last_verified": "2026-11-08",
            "product_url": "https://example.org/shop"
        }
        self.today = date(2026, 11, 8)

    def check(self):
        return guard.assess(self.product, today=self.today)

    def test_valid_product(self):
        self.assertEqual(self.check()["decision"], "PROMOTE")

    def test_out_of_stock(self):
        self.product["stock"] = 0
        self.assertEqual(self.check()["decision"], "DO_NOT_PROMOTE")

    def test_supplier_unverified(self):
        self.product.update(stock_policy="supplier", supplier_verified=False)
        self.assertEqual(self.check()["decision"], "DO_NOT_PROMOTE")

    def test_below_margin_floor(self):
        self.assertEqual(guard.assess(self.product, today=self.today, min_margin_pct=50)["decision"], "DO_NOT_PROMOTE")

    def test_stale_verification(self):
        self.product["last_verified"] = "2026-01-01"
        self.assertEqual(self.check()["decision"], "DO_NOT_PROMOTE")

    def test_unverified_fulfillment(self):
        self.product.update(fulfillment="manual", fulfillment_capacity_verified=False)
        self.assertEqual(self.check()["decision"], "DO_NOT_PROMOTE")

    def test_bad_inventory(self):
        self.product["stock"] = 1.2
        self.assertEqual(self.check()["decision"], "DO_NOT_PROMOTE")

    def test_duplicate_skus(self):
        with self.assertRaises(ValueError):
            guard.analyze({"products": [self.product, self.product]}, today=self.today)

if __name__ == "__main__":
    unittest.main()
