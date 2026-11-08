"""Regression: only comparable first-party baselines reach Trial decisions."""
import unittest
from datetime import date, timedelta
from pathlib import Path
import importlib.util

ROOT=Path(__file__).resolve().parents[1] / "skills" / "instagram-brand-director"
def module(name,filename):
    spec=importlib.util.spec_from_file_location(name,ROOT/"scripts"/filename)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

build=module("baseline_builder","baseline_builder.py")
validate=module("validator","validate_data.py")
trial=module("trial_review_for_baseline","trial_review.py")
HEADER="post_id,published_at,format,goal,reach,likes,shares,saves,follows,trial,sku,source,metrics_age_hours"

def posts(n, age="72", source="meta_insights_export_001", reach=500):
    lines=[HEADER]
    for i in range(n):
        day=date(2026,10,1)+timedelta(days=i)
        lines.append(f"p{i},{day}T16:00:00+03:30,reel,discovery,{reach},40,5,7,1,false,,{source},{age}")
    return "\n".join(lines)+"\n"

class BaselineTests(unittest.TestCase):
    def setUp(self):
        self.brand=validate.read_md(ROOT/"templates"/"brand.md")
        self.brand["primary_goal"]="discovery"
        self.args=dict(as_of=date(2026,11,9),start=date(2026,10,1),
                       human_reviewed_comparability=True)

    def test_pooled_rate_not_mean_of_rates(self):
        csv=posts(8)
        out=build.compile_baseline(self.brand,csv,**self.args)
        self.assertEqual(out["status"],"READY_FOR_OPERATIONAL_COMPARISON")
        self.assertTrue(out["comparable"])
        self.assertEqual(out["n_comparable_posts"],8)
        self.assertEqual(out["total_reach"],4000)
        self.assertAlmostEqual(out["shares_per_reach"],.01)

    def test_no_human_review_stays_insufficient(self):
        out=build.compile_baseline(self.brand,posts(8),as_of=self.args["as_of"],
             start=self.args["start"])
        self.assertEqual(out["status"],"INSUFFICIENT_DATA")
        self.assertFalse(out["comparable"])

    def test_two_posts_stay_inconclusive(self):
        out=build.compile_baseline(self.brand,posts(2),**self.args)
        self.assertFalse(out["comparable"])
        self.assertTrue(any("Only 2" in x for x in out["evidence_gaps"]))

    def test_age_mismatch_rejects_comparison(self):
        out=build.compile_baseline(self.brand,posts(8,age="300"),**self.args)
        self.assertFalse(out["comparable"])

    def test_sample_data_rejected(self):
        with self.assertRaises(ValueError):
            build.compile_baseline(self.brand,posts(8,source="example_only"),**self.args)

    def test_incomplete_or_fabricated_post_data_fails_validation(self):
        broken=posts(8).replace(",5,7,1,",",,7,1,")
        with self.assertRaises(ValueError):
            build.compile_baseline(self.brand,broken,**self.args)

    def test_trial_consumes_reviewed_baseline(self):
        b=build.compile_baseline(self.brand,posts(8),**self.args)
        t={"trial_available":True,"is_trial":True,"hours_since_publish":80,"reach":1000,"shares":20}
        p={"minimum_reach":300,"minimum_comparable_posts":6,"minimum_baseline_reach":1800,
           "primary_metric":"shares_per_reach","minimum_relative_to_baseline":1.2}
        self.assertEqual(trial.review(t,b,p)["decision"],"RECOMMEND_SHARE_WITH_EVERYONE")
        b["comparable"]=False
        self.assertEqual(trial.review(t,b,p)["decision"],"INSUFFICIENT_DATA")

    def test_ratio_can_exceed_one_due_to_multiple_shares(self):
        b=build.compile_baseline(self.brand,posts(8),**self.args)
        b["shares_per_reach"]=1.15
        self.assertEqual(validate.validate_baseline(b),[])

if __name__=="__main__": unittest.main()
