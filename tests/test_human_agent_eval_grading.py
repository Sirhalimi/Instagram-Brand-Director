"""Offline tests of human-attested response grading; no model is invoked.

All sample responses, review forms, and fabricated run records are synthetic.
A synthetic PASS in these unit tests is NOT a real agent behavior result.
"""
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BEHAVIOR=ROOT/"tests/behavior"
GRADER=ROOT/"tools/grade_agent_eval.py"
RUNNER=ROOT/"tools/run_agent_eval.py"

def import_file(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

g=import_file("igbd_human_grader",GRADER)
r=import_file("igbd_runner_for_grading",RUNNER)

def fake_case():
    return json.loads((BEHAVIOR/"phase5_sold_out_fa.json").read_text(encoding="utf-8"))

def synthetic_answer(case):
    return ("DO_NOT_PROMOTE: موجودی صفر است. فروش فوری را انجام نمی‌دهیم. "
            "برای جلوگیری از ناامیدی خریدار، به‌جای خرید فوری، "
            "لیست انتظار واقعی پیشنهاد می‌کنم.\n"
            "پیشنهاد جایگزین صرفاً پس از تأیید موجودی ارائه می‌شود.")

def fake_record(case,answer):
    return {"id":case["id"],"mode":"run","status":"RESPONSE_CAPTURED",
            "exit_code":0,"output":answer,
            "answer_sha256":hashlib.sha256(answer.encode()).hexdigest(),
            "prompt_sha256":hashlib.sha256("synthetic prompt".encode()).hexdigest(),
            "skill_snapshot_sha256":"a"*64}

def reviewed(case,answer):
    result=g.make_template(case)
    result["reviewer"]="Synthetic Test Reviewer"
    result["reviewed_at"]="2026-11-09T12:00:00+00:00"
    result["reviewed_full_response"]=True
    for c in result["criteria"]:
        c.update(verdict="met",evidence_quote="موجودی صفر است",
                 note="Synthetic positive unit-test evidence only")
    for f in result["forbidden"]:
        f.update(verdict="absent",note="Synthetic complete-response check")
    return result

class GradeEvalTests(unittest.TestCase):
    def setUp(self):
        self.case=fake_case()
        self.answer=synthetic_answer(self.case)
        self.record=fake_record(self.case,self.answer)
        self.review=reviewed(self.case,self.answer)

    def test_six_fixtures_have_reviewable_positive_and_forbidden_claims(self):
        for file in BEHAVIOR.glob("*.json"):
            case=json.loads(file.read_text(encoding="utf-8"))
            tmpl=g.make_template(case)
            self.assertEqual(tmpl["fixture_id"],case["id"])
            self.assertFalse(tmpl["reviewed_full_response"])
            self.assertEqual(len(tmpl["criteria"]),len(case["agent_expectations"]))
            self.assertEqual(len(tmpl["forbidden"]),len(case["forbidden_outcomes"]))
            self.assertTrue(all(x["verdict"]=="unclear" for x in tmpl["criteria"]))
            self.assertTrue(all(x["verdict"]=="unclear" for x in tmpl["forbidden"]))

    def test_never_auto_passes_unreviewed_response(self):
        result=g.make_template(self.case)
        with self.assertRaisesRegex(ValueError,"reviewer"):
            g.grade(self.case,self.record,self.answer,result)

    def test_explicitly_reviewed_synthetic_pass_is_human_attested(self):
        result=g.grade(self.case,self.record,self.answer,self.review,prompt="synthetic prompt")
        self.assertEqual(result["verdict"],"PASS")
        self.assertEqual(result["grade_type"],"HUMAN_ATTESTED_NOT_AUTOMATED")
        self.assertTrue(result["reviewed_full_response"])
        self.assertEqual(len(result["criteria"]),len(self.case["agent_expectations"]))
        self.assertTrue(result["limitations"])

    def test_failed_criterion_makes_explicit_fail(self):
        self.review["criteria"][0].update(verdict="not_met",evidence_quote="",
                                          note="The expected rejection was absent")
        out=g.grade(self.case,self.record,self.answer,self.review)
        self.assertEqual(out["verdict"],"FAIL")
        self.assertTrue(out["failures"])

    def test_forbidden_behavior_makes_fail_even_if_all_criteria_met(self):
        self.review["forbidden"][0].update(verdict="present",
                                           evidence_quote="فروش فوری",
                                           note="Synthetic example of prohibited CTA")
        out=g.grade(self.case,self.record,self.answer,self.review)
        self.assertEqual(out["verdict"],"FAIL")
        self.assertIn("forbidden",out["failures"][0])

    def test_unclear_is_not_a_pass(self):
        self.review["forbidden"][1].update(verdict="unclear",
                                           note="Cannot rule out misrepresentation")
        out=g.grade(self.case,self.record,self.answer,self.review)
        self.assertEqual(out["verdict"],"NEEDS_REVIEW")

    def test_quote_must_exist_in_actual_answer(self):
        self.review["criteria"][0]["evidence_quote"]="this quote was invented"
        with self.assertRaisesRegex(ValueError,"not found"):
            g.grade(self.case,self.record,self.answer,self.review)

    def test_critical_quote_is_required_for_met_and_present(self):
        self.review["criteria"][0]["evidence_quote"]=""
        with self.assertRaisesRegex(ValueError,"quote required"):
            g.grade(self.case,self.record,self.answer,self.review)
        self.review=reviewed(self.case,self.answer)
        self.review["forbidden"][0].update(verdict="present",
                                           evidence_quote="",note="Some forbidden claim")
        with self.assertRaisesRegex(ValueError,"quote required"):
            g.grade(self.case,self.record,self.answer,self.review)

    def test_cannot_grade_prepare_run_failure_or_no_answer(self):
        for changes in ({"mode":"prepare","status":"PREPARED_NO_MODEL_EXECUTION"},
                        {"status":"RUN_FAILED","exit_code":1},
                        {"status":"TIMEOUT","exit_code":None}):
            record={**self.record,**changes}
            with self.subTest(changes=changes),self.assertRaisesRegex(ValueError,"NOT_RUN"):
                g.grade(self.case,record,self.answer,self.review)

    def test_cannot_forge_pass_by_editing_transcript_or_sha(self):
        with self.assertRaisesRegex(ValueError,"does not match"):
            g.grade(self.case,self.record,self.answer+" Buy now!",self.review)
        wrong={**self.record,"answer_sha256":"0"*64}
        with self.assertRaisesRegex(ValueError,"SHA256"):
            g.grade(self.case,wrong,self.answer,self.review)
        with self.assertRaisesRegex(ValueError,"Prompt SHA256"):
            g.grade(self.case,self.record,self.answer,self.review,prompt="altered prompt")

    def test_wrong_fixture_or_incomplete_judgment_cannot_pass(self):
        self.review["fixture_id"]="different"
        with self.assertRaisesRegex(ValueError,"ID mismatch"):
            g.grade(self.case,self.record,self.answer,self.review)
        self.review=reviewed(self.case,self.answer)
        self.review["criteria"].pop()
        with self.assertRaisesRegex(ValueError,"cover every"):
            g.grade(self.case,self.record,self.answer,self.review)

    def test_duplicate_index_and_invalid_verdict_rejected(self):
        self.review["criteria"][1]["index"]=0
        with self.assertRaisesRegex(ValueError,"unique"):
            g.grade(self.case,self.record,self.answer,self.review)
        self.review=reviewed(self.case,self.answer)
        self.review["criteria"][0]["verdict"]="pass"
        with self.assertRaisesRegex(ValueError,"verdict"):
            g.grade(self.case,self.record,self.answer,self.review)

    def test_cli_template_is_nonpassing_and_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"review.json"
            command=[sys.executable,str(GRADER),
                     "--fixture",str(BEHAVIOR/"phase5_sold_out_fa.json"),
                     "--make-template",str(path)]
            first=subprocess.run(command,capture_output=True,text=True,timeout=15)
            self.assertEqual(first.returncode,0,first.stderr)
            self.assertEqual(json.loads(first.stdout)["verdict"],"NOT_GRADED")
            self.assertFalse(json.loads(path.read_text())["reviewed_full_response"])
            before=path.read_bytes()
            second=subprocess.run(command,capture_output=True,text=True,timeout=15)
            self.assertEqual(second.returncode,2)
            self.assertEqual(path.read_bytes(),before)

    def test_cli_grade_uses_explicit_files_only(self):
        with tempfile.TemporaryDirectory() as temp:
            home=Path(temp)
            fixture=home/"fixture.json"
            record=home/"record.json"
            answer=home/"answer.txt"
            review=home/"review.json"
            output=home/"grade.json"
            fixture.write_text(json.dumps(self.case),encoding="utf-8")
            record.write_text(json.dumps(self.record),encoding="utf-8")
            answer.write_text(self.answer,encoding="utf-8")
            review.write_text(json.dumps(self.review),encoding="utf-8")
            command=[sys.executable,str(GRADER),
                     "--fixture",str(fixture),
                     "--record",str(record),
                     "--answer",str(answer),
                     "--review",str(review),
                     "--output",str(output)]
            passed=subprocess.run(command,capture_output=True,text=True,timeout=15)
            self.assertEqual(passed.returncode,0,passed.stderr)
            self.assertEqual(json.loads(output.read_text())["verdict"],"PASS")
            again=subprocess.run(command,capture_output=True,text=True,timeout=15)
            self.assertEqual(again.returncode,2)
            self.assertEqual(json.loads(output.read_text())["verdict"],"PASS")

    def test_runner_prepares_matching_skill_and_prompt_hashes(self):
        with tempfile.TemporaryDirectory() as temp:
            result=r.execute(fixtures=BEHAVIOR,mode="prepare",
                             case_ids=["phase5_sold_out_fa"],output=Path(temp)/"out")
            self.assertFalse(result["actual_model_executed"])
            self.assertEqual(result["captured_response_count"],0)
            item=result["cases"][0]
            self.assertEqual(item["prompt_sha256"],
                hashlib.sha256(Path(item["prompt_file"]).read_bytes()).hexdigest())
            self.assertEqual(len(item["skill_snapshot_sha256"]),64)
            self.assertEqual(item["status"],"PREPARED_NO_MODEL_EXECUTION")

    def test_runner_refuses_reusing_old_results_dir(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/"out"
            r.execute(fixtures=BEHAVIOR,output=out,mode="prepare",
                      case_ids=["phase5_sold_out_fa"])
            with self.assertRaisesRegex(ValueError,"new or empty"):
                r.execute(fixtures=BEHAVIOR,output=out,mode="prepare",
                          case_ids=["phase5_sold_out_fa"])

if __name__=="__main__":
    unittest.main()
