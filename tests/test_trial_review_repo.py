"""Offline trial review regression: uncertainty and small samples are first-class."""
import importlib.util
import unittest
from pathlib import Path
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "trial_review.py"
spec = importlib.util.spec_from_file_location("trial_review", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class TrialReviewTests(unittest.TestCase):
    def setUp(self):
        self.trial = {"trial_available": True, "is_trial": True, "hours_since_publish": 26,
                      "reach": 1000, "shares": 20}
        self.baseline = {"shares_per_reach": 0.01, "n_comparable_posts": 8,
                         "total_reach": 7800, "comparable": True}
        self.policy = {"minimum_reach": 300, "minimum_comparable_posts": 6,
                       "minimum_baseline_reach": 1800,
                       "primary_metric": "shares_per_reach",
                       "minimum_relative_to_baseline": 1.2}

    def decision(self):
        return module.review(self.trial, self.baseline, self.policy)

    def test_sufficient_trial_is_operational_not_learning(self):
        result = self.decision()
        self.assertEqual(result["decision"], "RECOMMEND_SHARE_WITH_EVERYONE")
        self.assertFalse(result["learning_eligible"])
        self.assertFalse(result["executed"])

    def test_early_review(self):
        self.trial["hours_since_publish"] = 8
        self.assertEqual(self.decision()["decision"], "WAIT_FOR_FIRST_REVIEW")

    def test_missing_metric(self):
        del self.trial["shares"]
        self.assertEqual(self.decision()["decision"], "INSUFFICIENT_DATA")

    def test_low_reach_at_80h_is_not_a_negative_result(self):
        self.trial.update(reach=50, hours_since_publish=80)
        result=self.decision()
        self.assertEqual(result["decision"], "INSUFFICIENT_DATA")
        self.assertFalse(result["learning_eligible"])

    def test_two_baseline_posts_are_noise(self):
        self.baseline["n_comparable_posts"] = 2
        self.assertEqual(self.decision()["decision"], "INSUFFICIENT_DATA")

    def test_baseline_missing_count_is_not_assumed(self):
        del self.baseline["n_comparable_posts"]
        self.assertEqual(self.decision()["decision"], "INSUFFICIENT_DATA")

    def test_baseline_missing_pool_is_not_assumed(self):
        del self.baseline["total_reach"]
        self.assertEqual(self.decision()["decision"], "INSUFFICIENT_DATA")

    def test_baseline_not_comparable(self):
        self.baseline["comparable"] = False
        self.assertEqual(self.decision()["decision"], "INSUFFICIENT_DATA")

    def test_baseline_zero(self):
        self.baseline["shares_per_reach"] = 0
        self.assertEqual(self.decision()["decision"], "INSUFFICIENT_DATA")

    def test_underperforming_after_72h_with_sufficient_data(self):
        self.trial.update(hours_since_publish=80, shares=1)
        self.assertEqual(self.decision()["decision"], "REWORK_NEXT_CREATIVE")

    def test_invalid_min_reach(self):
        self.policy["minimum_reach"] = True
        with self.assertRaises(ValueError):
            self.decision()

    def test_unavailable(self):
        self.trial["trial_available"] = False
        self.assertEqual(self.decision()["decision"], "MANUAL_NORMAL_REEL")

if __name__ == "__main__":
    unittest.main()
