"""Different business types must produce capacity- and economics-aware decisions."""
import json, unittest
from datetime import date
from pathlib import Path
from scripts.campaign_decision import decide

ROOT=Path(__file__).resolve().parents[1]
class CrossBrandTests(unittest.TestCase):
    def test_five_synthetic_brand_decisions(self):
        cases=json.loads((ROOT/"evals/synthetic-brands.json").read_text(encoding="utf8"))["cases"]
        self.assertGreaterEqual(len({x["brand_kind"] for x in cases}),4)
        for case in cases:
            with self.subTest(case=case["id"]):
                out=decide(case["brief"],today=date(2026,11,9))
                self.assertEqual(out["decision"],case["expected_decision"])
                self.assertTrue(out["human_approval_required"])
                self.assertFalse(out["executed"])
                self.assertTrue(out["why"])
                self.assertTrue(out["next_action"])
    def test_synthetic_profiles_are_not_real_brands(self):
        content=(ROOT/"evals/synthetic-brands.json").read_text(encoding="utf8")
        self.assertIn("Synthetic",content)
        self.assertNotIn("api_key",content.lower())
if __name__=="__main__":unittest.main()
