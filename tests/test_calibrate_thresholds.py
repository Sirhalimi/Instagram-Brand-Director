"""Phase 1 thresholds calibrated from synthetic brand CSV, no real client records."""
import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from scripts.calibrate_thresholds import (
    DEFAULT_THRESHOLDS, parse_posts_csv, calibrate, derive_min_posts, propose)

HEADER = ("date,format,topic,hook,duration_s,trial,reach,"
          "non_follower_share,watch_time,sends,saves,likes,follows_gained")

def csv_for(days, reach=500, fmt="reel", all_zero=False):
    lines = [HEADER]
    start = date(2026, 1, 1)
    for i, day in enumerate(days):
        d = (start + timedelta(days=day)).isoformat()
        vals = (0, 0, 0, 0) if all_zero else (5, 10, 40, 2)
        lines.append(f"{d},{fmt},editorial,three_mistakes,18,false,{reach},0.7,8,"
                     f"{vals[0]},{vals[1]},{vals[2]},{vals[3]}")
    return "\n".join(lines) + "\n"

class CalibrationTests(unittest.TestCase):
    def test_dormancy_calibrates_with_posting_cadence(self):
        fast = calibrate(parse_posts_csv(csv_for([0, 1, 2, 3, 4, 5])),
                         today=date(2026, 11, 9))
        slow = calibrate(parse_posts_csv(csv_for([0, 15, 30, 45, 60, 75])),
                         today=date(2026, 11, 9))
        f = fast["thresholds"]["dormant_after_days"]
        s = slow["thresholds"]["dormant_after_days"]
        self.assertEqual(f["value"], 30)
        self.assertEqual(s["value"], 60)
        self.assertEqual(f["source"], "derived")
        self.assertEqual(s["source"], "derived")
        self.assertEqual(s["evidence"]["median_gap_days"], 15.0)

    def test_sparse_brand_retains_default_low_confidence(self):
        result = calibrate(parse_posts_csv(csv_for([0, 4, 8])), today=date(2026, 11, 9))
        for key, expected in DEFAULT_THRESHOLDS.items():
            self.assertEqual(result["thresholds"][key]["value"], expected)
            self.assertEqual(result["thresholds"][key]["source"], "default")
            self.assertEqual(result["thresholds"][key]["confidence"], "low")
        self.assertEqual(result["ghost_self_baseline"]["status"], "insufficient_data")
        self.assertEqual(result["ghost_self_baseline"]["ghost_risk"], "unknown")

    def test_stable_per_reach_medians_find_smallest_n(self):
        data = calibrate(parse_posts_csv(csv_for(range(16))), today=date(2026, 11, 9))
        threshold = data["thresholds"]["min_posts_for_baseline_by_format"]["reel"]
        self.assertEqual(threshold["source"], "derived")
        self.assertGreaterEqual(threshold["value"], 6)
        self.assertLessEqual(threshold["value"], 12)
        self.assertGreaterEqual(threshold["evidence"]["consecutive_steps"], 3)

    def test_all_zero_metrics_are_not_fake_stability(self):
        data = calibrate(parse_posts_csv(csv_for(range(16), all_zero=True)),
                         today=date(2026, 11, 9))
        entry = data["thresholds"]["min_posts_for_baseline_by_format"]["reel"]
        self.assertEqual(entry["source"], "default")
        self.assertIn("baseline unstable", entry["evidence"]["reason"])

    def test_incomplete_rows_cannot_force_derived_metric_minimum(self):
        text = csv_for(range(16)).replace(",5,10,40,2", ",,10,40,2")
        result = calibrate(parse_posts_csv(text), today=date(2026, 11, 9))
        entry = result["thresholds"]["min_posts_for_baseline_by_format"]["reel"]
        self.assertEqual(entry["source"], "default")

    def test_existing_config_never_overwritten_and_diff_printable(self):
        with tempfile.TemporaryDirectory() as dirname:
            p = Path(dirname)
            source = p / "posts.csv"
            source.write_text(csv_for(range(16)), encoding="utf-8")
            active = p / "config.json"
            original = '{"schema_version":1,"owner_note":"do_not_change"}\n'
            active.write_text(original, encoding="utf-8")
            outcome = propose(source, today=date(2026, 11, 9))
            self.assertEqual(active.read_text(encoding="utf-8"), original)
            self.assertEqual((p / "config.proposed.json").exists(), True)
            self.assertEqual(outcome["proposal"]["approval_status"], "proposed_not_active")
            self.assertIn("--- approved/config.json", outcome["diff"])
            self.assertIn("+++ proposed/config.proposed.json", outcome["diff"])
            with self.assertRaises(FileExistsError):
                propose(source, today=date(2026, 11, 9))

    def test_explicit_config_output_is_also_protected(self):
        with tempfile.TemporaryDirectory() as dirname:
            p = Path(dirname)
            posts = p / "posts.csv"
            posts.write_text(csv_for(range(6)), encoding="utf-8")
            config = p / "config.json"
            config.write_text('{"approved":true}', encoding="utf-8")
            with self.assertRaises(ValueError):
                propose(posts, output_path=config, today=date(2026, 11, 9))
            self.assertEqual(json.loads(config.read_text())["approved"], True)

    def test_dormant_with_older_active_period_has_self_baseline(self):
        data = calibrate(parse_posts_csv(csv_for(range(16))),
            growth={"earlier_active_period": {
                "start": "2026-01-01", "end": "2026-02-28",
                "followers": 800, "story_views_median": 120}},
            today=date(2026, 11, 9))
        ghost = data["ghost_self_baseline"]
        self.assertEqual(ghost["status"], "available")
        self.assertEqual(ghost["source"], "derived")
        self.assertEqual(ghost["n_earlier_posts"], 16)
        self.assertAlmostEqual(ghost["reach_per_follower"]["median"], 500/800, delta=1e-7)
        self.assertEqual(ghost["ghost_risk"], "unknown")

    def test_dormant_without_history_ghost_stays_unknown(self):
        result = calibrate(parse_posts_csv(csv_for(range(16))), today=date(2026, 11, 9))
        ghost = result["ghost_self_baseline"]
        self.assertEqual(ghost["status"], "insufficient_data")
        self.assertEqual(ghost["ghost_risk"], "unknown")

    def test_growth_without_historical_follower_denominator_is_insufficient(self):
        result = calibrate(parse_posts_csv(csv_for(range(16))),
            growth={"earlier_active_period":{"start":"2026-01-01","end":"2026-02-28"}},
            today=date(2026, 11, 9))
        self.assertEqual(result["ghost_self_baseline"]["status"], "insufficient_data")

    def test_invalid_post_dates_rejected_not_coerced(self):
        with self.assertRaises(ValueError):
            parse_posts_csv(csv_for([0,1,2]).replace("2026-01-02","not-a-date"))

    def test_derived_source_includes_evidence(self):
        result = calibrate(parse_posts_csv(csv_for(range(12))), today=date(2026, 11, 9))
        for name, rule in result["thresholds"].items():
            if name == "min_posts_for_baseline_by_format":
                for entry in rule.values():
                    if entry["source"] == "derived":
                        self.assertTrue(entry["evidence"])
            elif rule["source"] == "derived":
                self.assertTrue(rule["evidence"])

if __name__ == "__main__":
    unittest.main()
