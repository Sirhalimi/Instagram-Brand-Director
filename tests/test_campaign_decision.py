import unittest
from datetime import date
from scripts.campaign_decision import decide

TODAY = date(2026, 11, 9)

def brief(goal="discovery", **content):
    return {
        "brand": {"production_capabilities": ["filming_products", "static_design"], "paid_ads_enabled": False},
        "content": {"goal": goal, "preferred_format": "reel", "novel_concept": True,
                    "trial_available": True, "rights_verified": True, "claims_verified": True, **content},
        "commercial": {}
    }

def product():
    return {"sku": "A1", "name": "Sample", "status": "active", "currency": "USD",
            "stock_policy": "tracked", "stock": 8, "price": "100", "unit_cost": "60",
            "fulfillment": "automatic", "last_verified": "2026-11-09",
            "product_url": "https://example.org/p/A1"}

class CampaignTests(unittest.TestCase):
    def test_trial_for_novel_discovery(self):
        self.assertEqual(decide(brief(), today=TODAY)["decision"], "TRIAL_REEL")

    def test_time_sensitive_normal(self):
        self.assertEqual(decide(brief(time_sensitive=True), today=TODAY)["decision"], "NORMAL_REEL")

    def test_missing_trial_feature_requires_verification(self):
        self.assertEqual(decide(brief(trial_available=None), today=TODAY)["decision"], "VERIFY_TRIAL_ACCESS")

    def test_unavailable_trial_normal(self):
        self.assertEqual(decide(brief(trial_available=False), today=TODAY)["decision"], "NORMAL_REEL")

    def test_rights_block(self):
        self.assertEqual(decide(brief(rights_verified=False), today=TODAY)["decision"], "HOLD_CREATIVE")

    def test_no_face_adaptation(self):
        item = brief(requires_face=True)
        self.assertEqual(decide(item, today=TODAY)["decision"], "REWORK_FACELESS")

    def test_video_not_possible_carousel(self):
        item = brief()
        item["brand"]["production_capabilities"] = ["static_design"]
        self.assertEqual(decide(item, today=TODAY)["decision"], "CAROUSEL")

    def test_conversion_product_missing(self):
        self.assertEqual(decide(brief(goal="conversion"), today=TODAY)["decision"], "REQUEST_CRITICAL_DATA")

    def test_conversion_out_of_stock(self):
        item = brief(goal="conversion")
        item["commercial"]["product"] = product()
        item["commercial"]["product"]["stock"] = 0
        self.assertEqual(decide(item, today=TODAY)["decision"], "DO_NOT_PROMOTE")

    def test_conversion_active(self):
        item = brief(goal="conversion")
        item["commercial"]["product"] = product()
        self.assertEqual(decide(item, today=TODAY)["decision"], "NORMAL_REEL")

    def test_paid_execution_disabled(self):
        item = brief(goal="conversion")
        item["commercial"] = {"product": product(), "paid_execution_requested": True}
        self.assertEqual(decide(item, today=TODAY)["decision"], "PAID_ADS_DISABLED")

    def test_paid_cost_unknown(self):
        item = brief(goal="conversion")
        p = product()
        p.pop("unit_cost")
        item["commercial"] = {"product": p, "paid_execution_requested": True}
        self.assertEqual(decide(item, today=TODAY)["decision"], "HOLD_PAID_AD")

    def test_human_approval_flag(self):
        out = decide(brief(), today=TODAY)
        self.assertTrue(out["human_approval_required"])
        self.assertFalse(out["executed"])

    def test_malformed_capability(self):
        item = brief()
        item["brand"]["production_capabilities"] = "camera"
        with self.assertRaises(ValueError):
            decide(item, today=TODAY)

if __name__ == "__main__":
    unittest.main()
