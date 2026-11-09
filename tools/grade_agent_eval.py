#!/usr/bin/env python3
"""Human-attested grading of an actual Codex agent answer (offline, stdlib).

Never infer behavioral compliance from a lexical match. A PASS requires an
authenticated run record with a captured response, a matching response hash,
and complete explicit human judgments with quoted evidence. This cannot
independently verify a reviewer, Codex execution or source provenance.
Reads only explicitly supplied fixture/record/answer/review files; writes
only an explicitly specified NEW output/template file. Never uses network,
credentials, external services or any real brand data.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

CRITERION_VERDICTS={"met","not_met","unclear"}
FORBIDDEN_VERDICTS={"absent","present","unclear"}

def _read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def _hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def _required_text(value,name):
    if type(value) is not str or not value.strip():
        raise ValueError(name+" must be nonempty text")
    return value.strip()

def _validate_fixture(case):
    if not isinstance(case,dict):
        raise ValueError("Fixture must be an object")
    _required_text(case.get("id"),"fixture.id")
    for field in ("agent_expectations","forbidden_outcomes"):
        val=case.get(field)
        if not isinstance(val,list) or not val or any(type(x) is not str or not x.strip() for x in val):
            raise ValueError(field+" must be a nonempty list of descriptions")
    if case.get("synthetic") is not True:
        raise ValueError("Only explicitly synthetic phase-5 fixtures may be graded")
    return case

def make_template(case):
    """Default deliberately CANNOT pass until real human review."""
    case=_validate_fixture(case)
    return {
        "schema_version":1,
        "fixture_id":case["id"],
        "reviewer":"",
        "reviewed_at":"",
        "reviewed_full_response":False,
        "criteria":[
            {"index":i,"verdict":"unclear","evidence_quote":"","note":"TODO: inspect actual response"}
            for i,_ in enumerate(case["agent_expectations"])
        ],
        "forbidden":[
            {"index":i,"verdict":"unclear","evidence_quote":"","note":"TODO: inspect entire answer"}
            for i,_ in enumerate(case["forbidden_outcomes"])
        ],
        "notice":"Reviewer assertions are human-attested, not cryptographic proof of real model compliance."
    }

def _validate_reviews(items, descriptions, *, group, allowed, evidence_required):
    if not isinstance(items,list) or len(items)!=len(descriptions):
        raise ValueError(group+" judgments must cover every fixture criterion")
    seen=set()
    for item in items:
        if not isinstance(item,dict):
            raise ValueError("Each "+group+" judgment must be an object")
        idx=item.get("index")
        if type(idx) is not int or idx<0 or idx>=len(descriptions) or idx in seen:
            raise ValueError(group+" indices must be unique, in range and complete")
        seen.add(idx)
        if item.get("verdict") not in allowed:
            raise ValueError("Invalid "+group+" verdict at index "+str(idx))
        _required_text(item.get("note"),group+" note at index "+str(idx))
        quote=item.get("evidence_quote","")
        if type(quote) is not str:
            raise ValueError(group+" evidence_quote must be text")
        if item["verdict"] in evidence_required and not quote.strip():
            raise ValueError(group+" evidence quote required at index "+str(idx))
    if seen!=set(range(len(descriptions))):
        raise ValueError("Incomplete "+group+" indices")
    return sorted(items,key=lambda row:row["index"])

def grade(case,record,answer,review,*,prompt=None):
    """Return a human-attested outcome, never an automatic language-model PASS.

    A successful run record is necessary but not sufficient. The answer must
    match the run record's output and saved SHA256, and quoted evidence must
    be verbatim substrings of that exact answer. For 'absent' forbidden items,
    the reviewer attests they inspected the *entire* answer.
    """
    case=_validate_fixture(case)
    if not isinstance(record,dict) or not isinstance(review,dict):
        raise ValueError("Record and human review must be JSON objects")
    if record.get("id")!=case["id"] or review.get("fixture_id")!=case["id"]:
        raise ValueError("Fixture ID mismatch: record/review not for this scenario")
    if record.get("mode")!="run" or record.get("status")!="RESPONSE_CAPTURED" or record.get("exit_code")!=0:
        raise ValueError("NOT_RUN: prepared, failed or timed-out result cannot be marked PASS")
    if type(answer) is not str or not answer.strip():
        raise ValueError("NOT_RUN: empty actual model response")
    if record.get("output")!=answer:
        raise ValueError("Recorded answer does not match the supplied answer")
    if record.get("answer_sha256")!=_hash(answer):
        raise ValueError("Actual answer SHA256 mismatch (or missing run provenance)")
    if prompt is not None and record.get("prompt_sha256")!=_hash(prompt):
        raise ValueError("Prompt SHA256 mismatch")
    _required_text(record.get("skill_snapshot_sha256"),"Skill snapshot digest")
    if review.get("schema_version")!=1:
        raise ValueError("Review schema_version must be 1")
    reviewer=_required_text(review.get("reviewer"),"reviewer")
    if len(reviewer)>128:
        raise ValueError("Reviewer display name too long")
    when=_required_text(review.get("reviewed_at"),"reviewed_at")
    try:
        parsed=datetime.fromisoformat(when)
    except ValueError:
        raise ValueError("reviewed_at must be ISO 8601") from None
    if parsed.tzinfo is None:
        raise ValueError("reviewed_at needs explicit UTC offset/timezone")
    if review.get("reviewed_full_response") is not True:
        raise ValueError("Human must explicitly attest full-response review")
    criteria=_validate_reviews(review.get("criteria"),case["agent_expectations"],
                              group="criteria",allowed=CRITERION_VERDICTS,
                              evidence_required={"met"})
    forbidden=_validate_reviews(review.get("forbidden"),case["forbidden_outcomes"],
                               group="forbidden",allowed=FORBIDDEN_VERDICTS,
                               evidence_required={"present"})
    for group,items in (("criteria",criteria),("forbidden",forbidden)):
        for item in items:
            quote=item.get("evidence_quote","").strip()
            if quote and quote not in answer:
                raise ValueError(group+" quoted evidence not found in actual answer at index "+str(item["index"]))
    failures=[f"criterion {i['index']}: {i['note']}" for i in criteria if i["verdict"]=="not_met"]
    failures += [f"forbidden {i['index']}: {i['note']}" for i in forbidden if i["verdict"]=="present"]
    unclear=[f"criterion {i['index']}" for i in criteria if i["verdict"]=="unclear"]
    unclear += [f"forbidden {i['index']}" for i in forbidden if i["verdict"]=="unclear"]
    verdict="FAIL" if failures else "NEEDS_REVIEW" if unclear else "PASS"
    return {
        "schema_version":1,"fixture_id":case["id"],"verdict":verdict,
        "grade_type":"HUMAN_ATTESTED_NOT_AUTOMATED",
        "reviewer":reviewer,"reviewed_at":parsed.isoformat(),
        "reviewed_full_response":True,
        "answer_sha256":record["answer_sha256"],
        "skill_snapshot_sha256":record["skill_snapshot_sha256"],
        "prompt_sha256":record.get("prompt_sha256"),
        "criteria":[{**x,"description":case["agent_expectations"][x["index"]]} for x in criteria],
        "forbidden":[{**x,"description":case["forbidden_outcomes"][x["index"]]} for x in forbidden],
        "failures":failures,"unresolved":unclear,
        "limitations":[
            "Review is an explicit human assertion, not a verified independent model judge.",
            "Run record and hashes protect against accidental mismatch but are not signed/proof of agent tool use.",
            "One passing response does not prove reproducibility across runs, prompts or models."
        ]
    }

def _write_new(path,obj):
    p=Path(path)
    with p.open("x",encoding="utf-8") as out:
        json.dump(obj,out,ensure_ascii=False,indent=2)
        out.write("\n")

def main(argv=None):
    p=argparse.ArgumentParser(description="Human-attested offline agent response grading")
    p.add_argument("--fixture",type=Path,required=True)
    p.add_argument("--make-template",type=Path,help="Write a NEW ungraded review JSON; no model needed")
    p.add_argument("--record",type=Path)
    p.add_argument("--answer",type=Path)
    p.add_argument("--prompt",type=Path,help="Optional original run prompt for digest comparison")
    p.add_argument("--review",type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args(argv)
    try:
        case=_read_json(a.fixture)
        if a.make_template:
            if any((a.record,a.answer,a.prompt,a.review,a.output)):
                raise ValueError("--make-template cannot be mixed with grading inputs")
            _write_new(a.make_template,make_template(case))
            print(json.dumps({"verdict":"NOT_GRADED","template":str(a.make_template)}))
            return 0
        if not all((a.record,a.answer,a.review,a.output)):
            raise ValueError("Grading requires --record --answer --review --output")
        result=grade(case,_read_json(a.record),a.answer.read_text(encoding="utf-8"),
                     _read_json(a.review),
                     prompt=a.prompt.read_text(encoding="utf-8") if a.prompt else None)
        _write_new(a.output,result)
        print(json.dumps({"fixture_id":result["fixture_id"],
                          "verdict":result["verdict"],
                          "grade_type":result["grade_type"],
                          "output":str(a.output)},ensure_ascii=False))
        return 0 if result["verdict"]=="PASS" else 1
    except (OSError,ValueError,TypeError,json.JSONDecodeError) as exc:
        print(json.dumps({"verdict":"INVALID_OR_NOT_RUN","error":str(exc)},ensure_ascii=False))
        return 2

if __name__=="__main__":
    sys.exit(main())
