"""Offline regression tests for Trial Reel decision engine."""
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
        self.baseline = {"shares_per_reach": 0.01}
        self.policy = {"minimum_reach": 100, "primary_metric": "shares_per_reach",
                       "minimum_relative_to_baseline": 1.2}

    def test_successful_trial(self):
        result = module.review(self.trial, self.baseline, self.policy)
        self.assertEqual(result["decision"], "RECOMMEND_SHARE_WITH_EVERYONE")
        self.assertFalse(result["executed"])

    def test_early_review(self):
        self.trial["hours_since_publish"] = 8
        self.assertEqual(module.review(self.trial, self.baseline, self.policy)["decision"], "WAIT_FOR_FIRST_REVIEW")

    def test_missing_metric(self):
        del self.trial["shares"]
        self.assertEqual(module.review(self.trial, self.baseline, self.policy)["decision"], "COLLECT_DATA")

    def test_low_sample(self):
        self.trial["reach"] = 50
        self.assertEqual(module.review(self.trial, self.baseline, self.policy)["decision"], "KEEP_TRIAL_COLLECT_MORE_DATA")

    def test_underperforming_after_72h(self):
        self.trial.update(hours_since_publish=80, shares=1)
        self.assertEqual(module.review(self.trial, self.baseline, self.policy)["decision"], "REWORK_NEXT_CREATIVE")

    def test_invalid_policy(self):
        self.policy["minimum_reach"] = True
        with self.assertRaises(ValueError):
            module.review(self.trial, self.baseline, self.policy)

    def test_unavailable(self):
        self.trial["trial_available"] = False
        self.assertEqual(module.review(self.trial, self.baseline, self.policy)["decision"], "MANUAL_NORMAL_REEL")

if __name__ == "__main__":
    unittest.main()
