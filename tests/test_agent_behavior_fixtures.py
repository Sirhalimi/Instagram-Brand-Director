"""Fixed behavior fixtures: execute deterministic engines; do NOT fake LLM evaluation."""
import importlib.util, json, unittest
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/"skills/instagram-brand-director"

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

router=load("routing_probe",SKILL/"scripts/router_probe.py")
trial=load("trial_fixture",SKILL/"scripts/trial_review.py")
campaign=load("campaign_fixture",SKILL/"scripts/campaign_decision.py")

class BehaviorFixtureTests(unittest.TestCase):
    def test_every_fixture_matches_deterministic_contract(self):
        cases=json.loads((ROOT/"evals/agent-scenarios.json").read_text(encoding="utf8"))["scenarios"]
        self.assertGreaterEqual(len(cases),8)
        for case in cases:
            with self.subTest(scenario=case["id"]):
                route=router.route(case["prompt"],case.get("brand"))
                self.assertEqual(route["primary"],case["expected_route"])
                self.assertLessEqual(route["file_count"],4)
                self.assertLessEqual(route["module_count"],2)
                if "requires_camera_confirmation" in case:
                    self.assertEqual(route["needs_camera_confirmation"],case["requires_camera_confirmation"])
                if "expected_response_mode" in case:
                    self.assertEqual(route["response_mode"],case["expected_response_mode"])
                if case["kind"]=="trial":
                    r=trial.review(case["trial"],case["baseline"],case["policy"])
                    self.assertEqual(r["decision"],case["expected_decision"])
                    self.assertFalse(r["learning_eligible"])
                elif case["kind"]=="campaign":
                    r=campaign.decide(case["brief"],today=date(2026,11,9))
                    self.assertEqual(r["decision"],case["expected_decision"])
                    self.assertTrue(r["why"])
                    self.assertTrue(r["next_action"])
                self.assertTrue(case["agent_expectations"])
    def test_fixture_not_falsely_claimed_as_live_agent_eval(self):
        cases=json.loads((ROOT/"evals/agent-scenarios.json").read_text(encoding="utf8"))
        self.assertIn("full LLM transcript eval",cases["note"])
if __name__=="__main__": unittest.main()
