"""Phase 3: deterministic router, private post intake, status honesty and review gates.

Tests are synthetic. They are NOT live LLM behavior evaluations.
"""
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/"skills/instagram-brand-director"

def load(name,filename):
    spec=importlib.util.spec_from_file_location(name,SKILL/"scripts"/filename)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

router=load("phase3_router","router_probe.py")
intake=load("phase3_intake","post_intake.py")
review=load("phase3_review","review_gate.py")
validate=load("phase3_validate","validate_data.py")

class AccountPreflightRoutes(unittest.TestCase):
    def test_brand_strategy_requires_account_state_first(self):
        for text in ("Create a monthly content calendar",
                     "Review last month's Instagram insights",
                     "ریلز آزمایشی یا عادی بهتر است؟",
                     "How should we grow this Instagram brand?"):
            with self.subTest(text=text):
                r=router.route(text)
                self.assertTrue(r["account_state_required"])
                self.assertEqual(r["files"][1],"modules/00-account-state.md")
                self.assertEqual(r["account_state_gate"],"RUN_CLASSIFIER_OR_REQUEST_CRITICAL_DATA")
                self.assertLessEqual(r["file_count"],4)

    def test_specific_format_choice_loads_preflight(self):
        r=router.route("ریلز یا کاروسل برای برندم بهتره؟")
        self.assertTrue(r["account_state_required"])
        self.assertEqual(r["files"][1],"modules/00-account-state.md")

    def test_standalone_copy_does_not_force_analytics(self):
        for text in ("Write a caption for my sweatshirt", "یک کپشن کوتاه بنویس"):
            with self.subTest(text=text):
                r=router.route(text)
                self.assertFalse(r["account_state_required"])
                self.assertEqual(r["response_mode"],"production")
                self.assertEqual(r["file_count"],2)

    def test_sold_out_safety_rejection_is_immediate(self):
        r=router.route("برای محصول ناموجود یک کمپین فروش بساز")
        self.assertEqual(r["primary"],"11-commerce-funnel.md")
        self.assertFalse(r["account_state_required"])
        self.assertEqual(r["file_count"],2)

    def test_a_validated_state_can_be_reused(self):
        r=router.route("Create a monthly content calendar",
            {"account_state":{"state":"DORMANT","thresholds_used":{"dormant_after_days":{"value":60,"source":"default"}}}})
        self.assertEqual(r["account_state_gate"],"USE_VALIDATED_STATE")

    def test_state_question_is_not_two_loaded_copies(self):
        r=router.route("Please classify the account state")
        self.assertEqual(r["primary"],"00-account-state.md")
        self.assertEqual(r["files"],["SKILL.md","modules/00-account-state.md"])

    def test_platform_rules_load_knowledge_not_every_module(self):
        r=router.route("What do official Meta rules say about Trial Reels eligibility?")
        self.assertTrue(r["account_state_required"])
        self.assertIn("knowledge/instagram-rules.md",r["files"])
        self.assertLessEqual(r["file_count"],5)

class PerPostIntakeTests(unittest.TestCase):
    def setUp(self):
        self.brand=validate.read_md(SKILL/"templates/brand.md")

    def test_new_video_asks_missing_fields(self):
        result=intake.intake(self.brand,{"format":"reel"})
        self.assertEqual(result["status"],"NEEDS_INPUT")
        self.assertIn("camera_presenter",result["missing_fields"])
        self.assertIn("excluded_audience",result["missing_fields"])
        self.assertIn("post_goal",result["missing_fields"])

    def test_no_face_never_asks_presenter(self):
        self.brand["camera_policy"]="no"
        result=intake.intake(self.brand,{"format":"reel"})
        self.assertNotIn("camera_presenter",result["missing_fields"])
        self.assertEqual(result["resolved"]["camera_presenter"],"none")

    def test_caption_does_not_ask_camera(self):
        result=intake.intake(self.brand,{"format":"caption"})
        self.assertNotIn("camera_presenter",result["missing_fields"])

    def test_existing_verified_profile_answers_not_reasked(self):
        self.brand["target_audience"]="wholesale buyers in the region"
        self.brand["post_defaults"]={
            "camera_presenter":"the approved demonstrator",
            "excluded_audience":"retail shoppers",
            "post_goal":"sends",
            "production_capacity":"90 minutes with existing product footage"}
        result=intake.intake(self.brand,{"format":"reel"})
        self.assertEqual(result["status"],"READY")
        self.assertEqual(result["missing_fields"],[])
        self.assertEqual(result["resolved"]["target_audience"],"wholesale buyers in the region")

    def test_post_specific_answer_overrides_stable_default_without_changing_it(self):
        self.brand["post_defaults"]={"post_goal":"saves"}
        result=intake.intake(self.brand,{"format":"caption","post_goal":"sales"})
        self.assertEqual(result["resolved"]["post_goal"],"sales")
        self.assertEqual(self.brand["post_defaults"]["post_goal"],"saves")

    def test_invalid_goal_not_saved(self):
        with self.assertRaises(ValueError):
            intake.save_durable(Path("/synthetic/brand.md"),{"post_goal":"viral"},["post_goal"])

    def test_default_cli_reads_only_and_optional_save_is_explicit(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);brand=p/"brand.md";post=p/"post.json";answers=p/"answers.json"
            brand.write_text((SKILL/"templates/brand.md").read_text(encoding="utf-8"),encoding="utf-8")
            post.write_text(json.dumps({"format":"reel"}),encoding="utf-8")
            answers.write_text(json.dumps({"answers":{
                "post_goal":"saves","target_audience":"science students"},
                "durable_keys":["post_goal","target_audience"]}),encoding="utf-8")
            original=brand.read_bytes()
            cmd=[sys.executable,str(SKILL/"scripts/post_intake.py"),
                 "--brand",str(brand),"--post",str(post),"--answers",str(answers)]
            dry=subprocess.run(cmd,capture_output=True,text=True,timeout=15)
            self.assertEqual(dry.returncode,0,dry.stderr)
            self.assertEqual(brand.read_bytes(),original)
            saved=subprocess.run(cmd+["--save"],capture_output=True,text=True,timeout=15)
            self.assertEqual(saved.returncode,0,saved.stderr)
            self.assertTrue(json.loads(saved.stdout)["write_performed"])
            updated=validate.read_md(brand)
            self.assertEqual(updated["post_defaults"]["post_goal"],"saves")
            self.assertEqual(updated["post_defaults"]["target_audience"],"science students")
            self.assertNotIn("camera_presenter",updated["post_defaults"])
            again=intake.intake(updated,{"format":"caption"})
            self.assertNotIn("post_goal",again["missing_fields"])
            self.assertNotIn("target_audience",again["missing_fields"])

    def test_refuses_persisting_presenter_for_faceless_brand(self):
        self.brand["camera_policy"]="no"
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"brand.md"
            raw=(SKILL/"templates/brand.md").read_text(encoding="utf-8")
            opening=chr(96)*3+"json\n"
            old=validate.read_md(SKILL/"templates/brand.md")
            new=dict(old,camera_policy="no")
            raw=raw.replace(json.dumps(old,indent=2,ensure_ascii=False),json.dumps(new,indent=2,ensure_ascii=False))
            # construct a simple private synthetic file for this isolated test
            path.write_text(opening+json.dumps(new,indent=2,ensure_ascii=False)+
                            "\n"+chr(96)*3+"\n",encoding="utf-8")
            with self.assertRaises(ValueError):
                intake.save_durable(path,{"camera_presenter":"founder"},["camera_presenter"])

class StrategySampleGateTests(unittest.TestCase):
    def setUp(self):
        self.data={"format":"reel","n_comparable_posts":8,"total_reach":9000,
                   "verified_first_party":True,"comparable":True,
                   "account_state":"ACTIVE_WITH_BASELINE"}

    def test_default_twelve_blocks_eight_posts(self):
        r=review.assess(self.data)
        self.assertEqual(r["decision"],"INSUFFICIENT_DATA")
        self.assertEqual(r["minimum_comparable_posts"],12)
        self.assertEqual(r["threshold_source"],"default")
        self.assertFalse(r["learning_eligible"])

    def test_twelve_comparable_posts_only_eligible_for_human_review(self):
        self.data["n_comparable_posts"]=12
        r=review.assess(self.data)
        self.assertEqual(r["decision"],"CANDIDATE_FOR_HUMAN_REVIEW")
        self.assertFalse(r["learning_eligible"])

    def test_owner_approved_derived_format_threshold(self):
        config={"thresholds":{"min_posts_for_baseline_by_format":{
            "reel":{"value":6,"source":"derived","evidence":{"synthetic":True}}}}}
        r=review.assess(self.data,config)
        self.assertEqual(r["minimum_comparable_posts"],6)
        self.assertEqual(r["threshold_source"],"derived")
        self.assertEqual(r["decision"],"CANDIDATE_FOR_HUMAN_REVIEW")

    def test_dormant_and_unverified_block_conclusion(self):
        self.data["n_comparable_posts"]=20
        self.data["account_state"]="DORMANT"
        r=review.assess(self.data)
        self.assertEqual(r["decision"],"INSUFFICIENT_DATA")
        self.data["account_state"]="ACTIVE_WITH_BASELINE"
        self.data["verified_first_party"]=False
        self.assertEqual(review.assess(self.data)["decision"],"INSUFFICIENT_DATA")

    def test_review_gate_cli_rejects_proposal_as_approved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"input.json"
            config=Path(tmp)/"config.proposed.json"
            path.write_text(json.dumps(self.data),encoding="utf-8")
            config.write_text("{}",encoding="utf-8")
            result=subprocess.run([sys.executable,str(SKILL/"scripts/review_gate.py"),
                                   str(path),"--config",str(config)],
                                  capture_output=True,text=True,timeout=15)
            self.assertEqual(result.returncode,2)
            self.assertEqual(json.loads(result.stdout)["decision"],"INVALID")

class StatusContractTests(unittest.TestCase):
    def test_table_matches_machine_registry_and_has_sixteen_rows(self):
        status=json.loads((SKILL/"references/implementation-status.json").read_text(encoding="utf-8"))
        text=(SKILL/"SKILL.md").read_text(encoding="utf-8")
        rows=re.findall(r"^\| (\d{2}) [^|]*\| (implemented|spec-only|not-implemented) \|",text,re.M)
        self.assertEqual(len(rows),16)
        self.assertEqual(set(status["modules"].values()),{"implemented","spec-only","not-implemented"})
        for number,state in rows:
            matching=[v for k,v in status["modules"].items() if k.startswith(number+"-")]
            self.assertEqual(matching,[state])

    def test_no_live_feature_is_marked_implemented(self):
        s=json.loads((SKILL/"references/implementation-status.json").read_text(encoding="utf-8"))
        for k in ("live_instagram_oauth","live_insights_sync","instagram_publish",
                  "paid_ads_execution","real_agent_preflight_behavior_eval"):
            self.assertEqual(s["capabilities"][k],"not-implemented")

    def test_persian_review_guide_is_in_installed_skill(self):
        text=(SKILL/"references/persian-review-checklist.md").read_text(encoding="utf-8")
        for phrase in ("نیم‌فاصله","RTL","هشتگ","زیرنویس","محاوره"):
            self.assertIn(phrase,text)

if __name__=="__main__":
    unittest.main()
