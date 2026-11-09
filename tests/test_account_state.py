"""Phase 1 account-state classifications; synthetic observations only."""
import copy
import json
import unittest
from datetime import date, timedelta
from pathlib import Path

from scripts.account_state import DEFAULT_THRESHOLDS, classify, load_thresholds

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"

def example(name):
    return json.loads((EXAMPLES / ("account-state." + name + ".sample.json")).read_text(encoding="utf-8"))

def recent_posts(n=20, reach=500):
    today = date(2026, 11, 9)
    return [{"date": (today - timedelta(days=2 * (n-i))).isoformat(),
             "format": "reel", "reach": reach, "sends": 10,
             "likes": 50, "saves": 20, "follows_gained": 2}
            for i in range(n)]

class AccountStateTests(unittest.TestCase):
    def test_zero_followers_empty_history_is_cold_start(self):
        r = classify(example("zero-follower-editorial"))
        self.assertEqual(r["state"], "COLD_START")
        self.assertEqual(r["flags"]["trial_eligible"], "no")
        self.assertIn("NORMAL_REEL", r["next_action_codes"])
        self.assertEqual(r["thresholds_used"]["cold_start_max_followers"]["source"], "default")

    def test_dormant_ignores_old_engagement_baseline(self):
        r = classify(example("dormant-digital-store"))
        self.assertEqual(r["state"], "DORMANT")
        self.assertIsNone(r["baseline"])
        self.assertEqual(r["flags"]["ghost_risk_confidence"], "low")
        self.assertIn("RUN_REACTIVATION_WINDOW", r["next_action_codes"])
        self.assertTrue(r["flags"]["has_audience"])

    def test_established_has_robust_per_format_baseline(self):
        r = classify(example("established-wholesale"))
        self.assertEqual(r["state"], "ACTIVE_WITH_BASELINE")
        reel = r["baseline"]["reel"]
        self.assertEqual(reel["n_posts_with_reach"], 20)
        self.assertEqual(reel["rates"]["sends_per_reach"]["n"], 20)
        self.assertIn("mad", reel["rates"]["likes_per_reach"])
        self.assertIn("median", reel["rates"]["follows_per_reach"])
        self.assertLess(reel["reach"]["median"], 1000)

    def test_absent_followers_never_implies_zero(self):
        r = classify({"today": "2026-11-09", "posts": []})
        self.assertEqual(r["state"], "NO_DATA")
        self.assertEqual(r["missing_data"], ["followers"])
        self.assertEqual(r["next_action_codes"], ["REQUEST_CRITICAL_DATA"])
        self.assertEqual(r["flags"]["trial_eligible"], "unknown")

    def test_absent_post_history_is_no_data(self):
        r = classify({"today": "2026-11-09", "followers": 0})
        self.assertEqual(r["state"], "NO_DATA")
        self.assertEqual(r["missing_data"], ["posts"])

    def test_missing_post_dates_are_no_data(self):
        r = classify({"today": "2026-11-09", "followers": 500,
                      "posts": [{"format": "reel", "reach": 200}]})
        self.assertEqual(r["state"], "NO_DATA")
        self.assertIn("posts[].date", r["missing_data"])
        self.assertIn("REQUEST_CRITICAL_DATA", r["next_action_codes"])

    def test_missing_reach_is_not_zero_baseline(self):
        posts = [{"date": row["date"], "format": "reel", "likes": 40}
                 for row in recent_posts()]
        r = classify({"today": "2026-11-09", "followers": 1000, "posts": posts})
        self.assertEqual(r["state"], "ACTIVE_LOW_DATA")
        self.assertIsNone(r["baseline"])
        self.assertIn("posts[].reach", r["missing_data"])

    def test_missing_engagement_counts_remain_unknown(self):
        posts = [{"date": row["date"], "format": "reel", "reach": 500}
                 for row in recent_posts()]
        r = classify({"today": "2026-11-09", "followers": 1000, "posts": posts})
        self.assertEqual(r["state"], "ACTIVE_LOW_DATA")
        self.assertIsNone(r["baseline"])

    def test_manual_sample_20_no_percentage(self):
        r = classify({"today": "2026-11-09", "followers": 1000, "posts": recent_posts(),
                      "manual_follower_sample": {"n": 20, "suspicious_n": 8}})
        self.assertNotIn("sample_suspicious_pct", r["flags"])
        self.assertTrue(any("too small" in x.lower() for x in r["flags"]["ghost_risk_notes"]))
        self.assertEqual(r["flags"]["ghost_risk"], "unknown")

    def test_manual_sample_40_only_sample_percentage(self):
        r = classify({"today": "2026-11-09", "followers": 1000, "posts": recent_posts(),
                      "manual_follower_sample": {"n": 40, "suspicious_n": 12}})
        self.assertEqual(r["flags"]["sample_suspicious_pct"], 30.0)
        self.assertIn("sample only", r["flags"]["sample_percentage_scope"].lower())
        self.assertEqual(r["flags"]["ghost_risk"], "unknown")

    def test_approved_derived_config_changes_state_and_source(self):
        account = {"today": "2026-11-09", "followers": 120, "posts": []}
        self.assertEqual(classify(account)["state"], "ACTIVE_LOW_DATA")
        cfg = {"thresholds": {
            "cold_start_max_followers": {"value": 150, "source": "derived",
                                          "evidence": {"owner_review": "synthetic"}}}}
        r = classify(account, cfg)
        self.assertEqual(r["state"], "COLD_START")
        self.assertEqual(r["thresholds_used"]["cold_start_max_followers"]["source"], "derived")
        self.assertEqual(r["thresholds_used"]["cold_start_max_followers"]["value"], 150)

    def test_per_format_derived_minimum(self):
        account = {"today": "2026-11-09", "followers": 1100, "posts": recent_posts(10)}
        self.assertEqual(classify(account)["state"], "ACTIVE_LOW_DATA")
        cfg = {"thresholds": {"min_posts_for_baseline_by_format": {
            "reel": {"value": 8, "source": "derived", "evidence": {"stability": "synthetic"}}}}}
        r = classify(account, cfg)
        self.assertEqual(r["state"], "ACTIVE_WITH_BASELINE")
        self.assertEqual(r["thresholds_used"]["min_posts_for_baseline_by_format"]["reel"]["source"], "derived")

    def test_outlier_does_not_dominate_robust_baseline(self):
        account = {"today": "2026-11-09", "followers": 1500, "posts": recent_posts()}
        account["posts"][-1]["reach"] = 9000000
        account["posts"][-1]["likes"] = 9000000
        r = classify(account)
        self.assertEqual(r["state"], "ACTIVE_WITH_BASELINE")
        self.assertLess(r["baseline"]["reel"]["reach"]["median"], 1000)
        self.assertAlmostEqual(r["baseline"]["reel"]["rates"]["likes_per_reach"]["median"],
                               0.1, delta=0.001)

    def test_trial_eligibility_band_is_provisional(self):
        for followers, toggle, expected in [
            (199, True, "no"), (200, False, "unknown"),
            (999, True, "yes"), (1000, False, "unknown"), (1000, True, "yes")]:
            with self.subTest(followers=followers, toggle=toggle):
                r = classify({"followers": followers, "posts": [], "today": "2026-11-09",
                              "trial_toggle_seen_in_app": toggle})
                self.assertEqual(r["flags"]["trial_eligible"], expected)

    def test_restricted_account_blocks_trial(self):
        r = classify({"followers": 1600, "posts": [], "today": "2026-11-09",
                      "trial_toggle_seen_in_app": True,
                      "account_status": {"eligible_for_recommendations": False}})
        self.assertIs(r["flags"]["restricted"], True)
        self.assertEqual(r["flags"]["trial_eligible"], "no")

    def test_no_self_history_leaves_ghost_risk_unknown(self):
        r = classify({"followers": 1000, "posts": recent_posts(),
                      "today": "2026-11-09", "follower_growth_spike_flag": True,
                      "audience": {"top_countries": [{"country": "FR", "share": 0.8}],
                                   "target_countries": ["IR"]}})
        self.assertEqual(r["flags"]["ghost_risk"], "unknown")
        self.assertTrue(r["flags"]["ghost_risk_evidence"])

    def test_conflicting_config_fails_closed(self):
        with self.assertRaises(ValueError):
            load_thresholds({"thresholds": {"dormant_after_days": {
                "value": 20, "source": "derived"}}})

if __name__ == "__main__":
    unittest.main()
