"""Offline tests for optional REAL Codex agent-response evaluation harness."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("agent_eval_runner",ROOT/"tools"/"run_agent_eval.py")
h=importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)

class AgentEvalRunnerTests(unittest.TestCase):
    def test_preparation_requires_no_model_or_credentials(self):
        with tempfile.TemporaryDirectory() as temp:
            record=h.execute(output=Path(temp)/"out",mode="prepare")
            self.assertFalse(record["actual_model_executed"])
            self.assertGreaterEqual(record["case_count"],10)
            for item in record["cases"]:
                self.assertEqual(item["status"],"PREPARED_NO_MODEL_EXECUTION")
                prompt=Path(item["prompt_file"]).read_text(encoding="utf-8")
                self.assertNotIn('"expected_decision"',prompt)
                self.assertNotIn('"agent_expectations"',prompt)
                inst=Path(item["prompt_file"]).parent/"workspace/.agents/skills/instagram-brand-director"
                self.assertTrue((inst/"SKILL.md").is_file())
                self.assertFalse((inst/"tests").exists())
                self.assertFalse((inst/".github").exists())
            summary=json.loads((Path(temp)/"out/summary.json").read_text(encoding="utf8"))
            self.assertFalse(summary["actual_model_executed"])

    def test_run_requires_explicit_consumption_consent(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                h.execute(output=Path(temp)/"out",mode="run")

    def test_prompt_context_honors_locale_without_expected_answer(self):
        case=h.load_cases()[0]
        prompt=h.prompt_for_case(case)
        self.assertIn("Persian",prompt)
        self.assertIn("stock",prompt)
        self.assertNotIn("DO_NOT_PROMOTE",prompt)

    def test_mechanical_grade_cannot_pass_as_human_eval(self):
        case=h.load_cases()[0]
        result=h.score_conservative(case,"DO_NOT_PROMOTE. No sale until stock returns.")
        self.assertEqual(result["mechanical_gate"],"PASS")
        self.assertTrue(result["human_review_required"])
        result=h.score_conservative(case,"حتماً این محصول را تبلیغ کنیم!")
        self.assertEqual(result["mechanical_gate"],"FLAG_FOR_REVIEW")

    def test_bad_case_ids_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                h.execute(output=Path(temp)/"out",case_ids=["bogus_id"])

if __name__=="__main__":unittest.main()
