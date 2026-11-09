"""Phase 5: six synthetic agent-behavior contract fixtures.

The assertions cover deterministic route/decision/input gates, NOT actual
generated-language compliance. Future model eval uses the same fixtures with
rubric.json kept outside the model's prompt/workspace for human grading.
"""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/instagram-brand-director"
BEHAVIOR = ROOT / "tests/behavior"

def import_file(alias, path):
    spec = importlib.util.spec_from_file_location(alias, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

account = import_file("phase5_account", ROOT / "scripts/account_state.py")
campaign = import_file("phase5_campaign", ROOT / "scripts/campaign_decision.py")
router = import_file("phase5_router", SKILL / "scripts/router_probe.py")
intake = import_file("phase5_intake", SKILL / "scripts/post_intake.py")
review = import_file("phase5_review", ROOT / "scripts/review_gate.py")
validate = import_file("phase5_validator", SKILL / "scripts/validate_data.py")
runner = import_file("phase5_runner", ROOT / "tools/run_agent_eval.py")

def fixtures():
    return {p.stem: json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(BEHAVIOR.glob("*.json"))}

class Phase5Fixtures(unittest.TestCase):
    def setUp(self):
        self.cases = fixtures()

    def test_six_synthetic_scenarios_with_explicit_manual_rubrics(self):
        self.assertEqual(set(self.cases), {
            "phase5_sold_out_fa", "phase5_faceless_en",
            "phase5_zero_followers_fa", "phase5_dormant_en",
            "phase5_camera_unknown_fa", "phase5_goal_conflict_en"
        })
        self.assertEqual({c["locale"] for c in self.cases.values()}, {"fa","en"})
        for name, item in self.cases.items():
            with self.subTest(name=name):
                self.assertEqual(item["id"], name)
                self.assertIs(item["synthetic"], True)
                self.assertTrue(item["prompt"].strip())
                self.assertGreaterEqual(len(item["agent_expectations"]), 2)
                self.assertGreaterEqual(len(item["forbidden_outcomes"]), 1)
                self.assertTrue(item["expected_route"].endswith(".md"))
                self.assertNotIn("api_key",json.dumps(item).lower())
                self.assertNotIn("access_token",json.dumps(item).lower())
                self.assertNotIn("password",json.dumps(item).lower())

    def test_router_contracts_per_scenario_without_all_module_loading(self):
        for name, item in self.cases.items():
            with self.subTest(name=name):
                r=router.route(item["prompt"],item.get("brand"))
                self.assertEqual(r["primary"],item["expected_route"])
                self.assertLessEqual(r["file_count"],5)
                self.assertLessEqual(r["module_count"],2)
        for name in ("phase5_zero_followers_fa","phase5_dormant_en",
                     "phase5_goal_conflict_en"):
            with self.subTest(name=name):
                r=router.route(self.cases[name]["prompt"],self.cases[name].get("brand"))
                self.assertTrue(r["account_state_required"])
                self.assertEqual(r["files"][1],"modules/00-account-state.md")
        self.assertFalse(router.route(self.cases["phase5_sold_out_fa"]["prompt"])
                         ["account_state_required"])

    def test_sold_out_refusal_is_automatic_even_if_owner_demands_sale(self):
        c=self.cases["phase5_sold_out_fa"]
        out=campaign.decide(c["brief"],today=date(2026,11,9))
        self.assertEqual(out["decision"],c["expected_decision"])
        self.assertEqual(out["commercial_preflight"]["decision"],"DO_NOT_PROMOTE")
        self.assertIn("stock",out["why"].lower())
        self.assertFalse(out["executed"])
        self.assertTrue(out["human_approval_required"])
        # An in-stock change must flip this specific stock guard.
        possible=json.loads(json.dumps(c["brief"]))
        possible["commercial"]["product"]["stock"]=2
        self.assertNotEqual(campaign.decide(possible,today=date(2026,11,9))["decision"],
                            "DO_NOT_PROMOTE")

    def test_faceless_campaign_requires_rewrite_not_talking_head(self):
        c=self.cases["phase5_faceless_en"]
        out=campaign.decide(c["brief"],today=date(2026,11,9))
        self.assertEqual(out["decision"],"REWORK_FACELESS")
        self.assertIn("footage",out["next_action"].lower())
        self.assertFalse(router.route(c["prompt"],c["brand"])["needs_camera_confirmation"])
        converted=json.loads(json.dumps(c["brief"]))
        converted["content"]["requires_face"]=False
        self.assertNotEqual(campaign.decide(converted,today=date(2026,11,9))["decision"],
                            "REWORK_FACELESS")

    def test_zero_followers_classifies_cold_start_and_chooses_normal_reel(self):
        c=self.cases["phase5_zero_followers_fa"]
        state=account.classify(c["account"])
        self.assertEqual(state["state"],c["expected_state"])
        self.assertEqual(state["flags"]["trial_eligible"],"no")
        self.assertIsNone(state["baseline"])
        out=campaign.decide(c["brief"],today=date(2026,11,9))
        self.assertEqual(out["decision"],"NORMAL_REEL")
        self.assertIn("NORMAL_REEL",state["next_action_codes"])
        missing=json.loads(json.dumps(c["account"]))
        missing.pop("posts")
        self.assertEqual(account.classify(missing)["state"],"NO_DATA")

    def test_dormant_prevents_stale_baseline_and_ghost_claims(self):
        c=self.cases["phase5_dormant_en"]
        out=account.classify(c["account"])
        self.assertEqual(out["state"],c["expected_state"])
        self.assertIsNone(out["baseline"])
        self.assertEqual(out["flags"]["ghost_risk"],c["expected_ghost_risk"])
        self.assertEqual(out["flags"]["ghost_risk_confidence"],"low")
        self.assertIn(c["expected_next_action"],out["next_action_codes"])
        self.assertTrue(any("stale" in x.lower() for x in out["reasons"]))
        recent=json.loads(json.dumps(c["account"]))
        recent["posts"][0]["date"]="2026-11-01"
        self.assertNotEqual(account.classify(recent)["state"],"DORMANT")

    def test_camera_unknown_asks_question_from_private_brand_profile(self):
        c=self.cases["phase5_camera_unknown_fa"]
        brand=validate.read_md(SKILL/"templates/brand.md")
        brand["primary_locale"]="fa"
        brand["camera_policy"]=c["brand"]["camera_policy"]
        result=intake.intake(brand,c["post"])
        self.assertEqual(result["status"],c["expected_intake_status"])
        self.assertEqual(result["missing_fields"],c["expected_missing_fields"])
        self.assertIn("camera_presenter",result["missing_fields"])
        self.assertIn("دوربین",result["questions"][0]["question"])
        self.assertFalse(result["write_performed"])
        self.assertTrue(router.route(c["prompt"],c["brand"])["needs_camera_confirmation"])
        brand["camera_policy"]="no"
        self.assertNotIn("camera_presenter",intake.intake(brand,c["post"])["missing_fields"])

    def test_owner_goal_conflict_has_insufficient_evidence_not_fake_learning(self):
        c=self.cases["phase5_goal_conflict_en"]
        state=account.classify(c["account"])
        self.assertEqual(state["state"],c["expected_state"])
        evidence=review.assess(c["review"])
        self.assertEqual(evidence["decision"],c["expected_decision"])
        self.assertEqual(evidence["minimum_comparable_posts"],12)
        self.assertTrue(any("2 independent" in text for text in evidence["reasons"]))
        self.assertFalse(evidence["learning_eligible"])
        # This is an actual conflict in the supplied data, not an LLM test.
        self.assertEqual(c["brand"]["primary_goal"],"conversion")
        self.assertIn("comedy",c["prompt"].lower())
        self.assertTrue(any("objection" in rule.lower()
                            for rule in c["agent_expectations"]))

    def test_directory_fixture_loading_is_compatible_with_eval_runner(self):
        cases=runner.load_cases(BEHAVIOR)
        self.assertEqual(len(cases),6)
        self.assertEqual({x["id"] for x in cases},set(self.cases))

    def test_prompt_includes_synthetic_account_but_hides_answer_key(self):
        for case in runner.load_cases(BEHAVIOR):
            with self.subTest(id=case["id"]):
                prompt=runner.prompt_for_case(case)
                self.assertIn(case["prompt"],prompt)
                self.assertNotIn('"expected_decision"',prompt)
                self.assertNotIn('"expected_state"',prompt)
                self.assertNotIn('"agent_expectations"',prompt)
                self.assertNotIn('"forbidden_outcomes"',prompt)
                if "account" in case:
                    self.assertIn('"followers"',prompt)
                if "post" in case:
                    self.assertIn('"post_id"',prompt)

    def test_preparation_is_cost_free_with_rubric_outside_agent_workspace(self):
        with tempfile.TemporaryDirectory() as temp:
            result=runner.execute(fixtures=BEHAVIOR,output=Path(temp)/"result",
                                  mode="prepare")
            self.assertEqual(result["case_count"],6)
            self.assertFalse(result["actual_model_executed"])
            for item in result["cases"]:
                self.assertEqual(item["status"],"PREPARED_NO_MODEL_EXECUTION")
                prompt=Path(item["prompt_file"])
                rubric=Path(item["rubric_file"])
                self.assertTrue(rubric.is_file())
                self.assertEqual(rubric.parent,prompt.parent)
                self.assertFalse((prompt.parent/"workspace/rubric.json").exists())
                self.assertTrue((prompt.parent/"workspace/.agents/skills/instagram-brand-director/SKILL.md").is_file())
                guide=json.loads(rubric.read_text(encoding="utf-8"))
                self.assertTrue(guide["human_review_required"])
                self.assertNotIn('"expected_route"',prompt.read_text(encoding="utf-8"))
                score=runner.score_conservative(self.cases[item["id"]],
                                                 "Everything is great, just do it!")
                self.assertEqual(score["mechanical_gate"],"NOT_GRADED")
                self.assertTrue(score["human_review_required"])

    def test_no_model_run_without_explicit_opt_in(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                runner.execute(fixtures=BEHAVIOR,output=Path(temp)/"result",
                               mode="run")

    def test_invalid_or_duplicate_fixture_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp)
            one=self.cases["phase5_sold_out_fa"]
            (directory/"first.json").write_text(json.dumps(one),encoding="utf-8")
            (directory/"second.json").write_text(json.dumps(one),encoding="utf-8")
            with self.assertRaises(ValueError):
                runner.load_cases(directory)

if __name__=="__main__":
    unittest.main()
