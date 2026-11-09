"""Packaged-skill integrity and deterministic behavior contracts.

These are NOT a substitute for evaluation of LLM-generated responses.
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/"skills"/"instagram-brand-director"

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

router=load("router_probe", SKILL/"scripts/router_probe.py")
validator=load("validate_data",SKILL/"scripts/validate_data.py")
trial=load("trial_packaged",SKILL/"scripts/trial_review.py")
learnings=load("learning_gate",SKILL/"scripts/learning_gate.py")

class SkillRoutingTests(unittest.TestCase):
    def test_single_module_for_caption_fa(self):
        x=router.route("برای برندم یک کپشن فارسی بنویس")
        self.assertEqual(x["primary"],"07-content-writing.md")
        self.assertEqual(x["file_count"],2)
        self.assertEqual(x["response_mode"],"production")
        self.assertFalse(x["needs_camera_confirmation"])

    def test_single_module_for_caption_en(self):
        x=router.route("Write a caption for my product")
        self.assertEqual(x["primary"],"07-content-writing.md")
        self.assertLessEqual(x["file_count"],3)

    def test_reel_unknown_camera_must_ask(self):
        x=router.route("Write a Reel for my brand")
        self.assertTrue(x["needs_camera_confirmation"])
        self.assertEqual(x["file_count"],2)

    def test_no_camera_does_not_ask_again(self):
        x=router.route("یه ریلز برای برند بدون چهره بنویس",{"camera_policy":"no"})
        self.assertEqual(x["primary"],"05-reels.md")
        self.assertFalse(x["needs_camera_confirmation"])

    def test_out_of_stock_preflight(self):
        x=router.route("برای محصول ناموجود یک کمپین فروش بساز")
        self.assertEqual(x["primary"],"11-commerce-funnel.md")
        self.assertEqual(x["file_count"],2)

    def test_trial_specialist_not_all_modules(self):
        x=router.route("تحلیل عملکرد ریلز آزمایشی بعد از ۷۲ ساعت")
        self.assertEqual(x["primary"],"06-trial-decisions.md")
        self.assertLessEqual(x["file_count"],3)

    def test_many_requests_stay_under_file_budget(self):
        prompts=["Write a caption", "Write a Reel for this product",
                 "Review last month's Instagram insights", "Research competitors",
                 "متن استوری می‌خوام", "دنبال آنالیز پیج هستم",
                 "چندتا ترند اینستاگرام پیشنهاد بده",
                 "مدیریت دایرکت پیج", "Trial Reel perform?", "Create a monthly content calendar"]
        for p in prompts:
            with self.subTest(p=p):
                x=router.route(p)
                self.assertLessEqual(x["module_count"],2)
                self.assertLessEqual(x["file_count"],4)
                self.assertTrue(all((SKILL/f).exists() for f in x["files"]))

class DataValidationTests(unittest.TestCase):
    def test_templates_valid_but_not_evidence(self):
        for name in ("brand","baseline"):
            r=validator.validate_file(name,SKILL/"templates"/f"{name}.md")
            self.assertTrue(r["valid"],r)
        baseline=validator.read_md(SKILL/"templates/baseline.md")
        self.assertEqual(baseline["n_comparable_posts"],0)
        self.assertFalse(baseline["comparable"])

    def test_posts_fixture_valid(self):
        r=validator.validate_file("posts",SKILL/"templates/posts.csv")
        self.assertTrue(r["valid"],r)

    def test_no_camera_conflict(self):
        b=validator.read_md(SKILL/"templates/brand.md")
        b["camera_policy"]="no"
        b["production_capabilities"].append("on_camera")
        self.assertTrue(validator.validate_brand(b))

    def test_future_unsupported_locale_fails_closed(self):
        b=validator.read_md(SKILL/"templates/brand.md")
        b["primary_locale"]="tr"
        self.assertTrue(validator.validate_brand(b))

    def test_posts_duplicate_id_fails(self):
        raw=(SKILL/"templates/posts.csv").read_text(encoding="utf8")
        head,record=raw.strip().splitlines()
        errors,count=validator.validate_posts_csv(head+"\n"+record+"\n"+record+"\n")
        self.assertTrue(errors)
        self.assertEqual(count,2)

    def test_missing_metrics_not_zero(self):
        raw=(SKILL/"templates/posts.csv").read_text(encoding="utf8").replace(",0,0,0,0,0,",",,0,0,0,0,")
        errors,_=validator.validate_posts_csv(raw)
        self.assertTrue(errors)

    def test_invalid_baseline_window(self):
        b=validator.read_md(SKILL/"templates/baseline.md")
        b["window_start"]="2027-01-01"
        self.assertTrue(validator.validate_baseline(b))

class SampleSizeTests(unittest.TestCase):
    def test_two_posts_trial_insufficient_even_after_72_hours(self):
        data=json.loads((ROOT/"examples/trial-review.sample.json").read_text())
        data["trial"]["hours_since_publish"]=80
        data["baseline"]["n_comparable_posts"]=2
        r=trial.review(data["trial"],data["baseline"],data["policy"])
        self.assertEqual(r["decision"],"INSUFFICIENT_DATA")
        self.assertFalse(r["learning_eligible"])

    def test_low_reach_even_after_72h_insufficient(self):
        data=json.loads((ROOT/"examples/trial-review.sample.json").read_text())
        data["trial"].update(reach=55,hours_since_publish=96)
        self.assertEqual(trial.review(data["trial"],data["baseline"],data["policy"])["decision"],"INSUFFICIENT_DATA")

    def test_learning_gate_prevents_one_post_memory(self):
        data=[{"post_id":"one","reach":1000,"comparable":True,"data_verified":True,
               "same_hypothesis":True,"major_confounder":False}]
        r=learnings.assess(data)
        self.assertEqual(r["status"],"INSUFFICIENT_DATA")
        self.assertFalse(r["can_write_learnings"])

    def test_sufficient_candidate_is_still_not_auto_written(self):
        data=[{"post_id":f"x{i}","reach":1100,"comparable":True,"data_verified":True,
               "same_hypothesis":True,"major_confounder":False} for i in range(4)]
        r=learnings.assess(data)
        self.assertEqual(r["status"],"CANDIDATE_FOR_HUMAN_REVIEW")
        self.assertFalse(r["can_write_learnings"])

class PackagingTests(unittest.TestCase):
    def test_sixteen_modules_including_account_state(self):
        # Intentional Phase-1 change: new module 00 increases the package to 16.
        self.assertEqual(len(list((SKILL/"modules").glob("*.md"))),16)
        self.assertTrue((SKILL/"modules/00-account-state.md").is_file())

    def test_package_has_no_repo_tooling(self):
        self.assertFalse((SKILL/".github").exists())
        self.assertFalse((SKILL/"tests").exists())
        self.assertTrue((SKILL/"SKILL.md").is_file())

    def test_packaged_cli_is_executable(self):
        cp=subprocess.run([sys.executable,"-m","scripts.trial_review",
            str(ROOT/"examples/trial-review.sample.json")],cwd=SKILL,
            capture_output=True,text=True,timeout=15)
        self.assertEqual(cp.returncode,0,cp.stderr)
        self.assertIn("learning_eligible",json.loads(cp.stdout))

    def test_status_registry_marks_live_features_not_implemented(self):
        s=json.loads((SKILL/"references/implementation-status.json").read_text())
        for key in ("live_instagram_oauth","live_insights_sync","instagram_publish","agent_runtime_eval"):
            self.assertEqual(s["capabilities"][key],"not-implemented")

if __name__=="__main__": unittest.main()
