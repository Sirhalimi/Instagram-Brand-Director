#!/usr/bin/env python3
"""Conservative strategy/learning baseline gate (NOT the one-off Trial gate).

Consult an explicit approved config only. Missing samples never count as zero.
Never writes files, never accesses a network or credentials. Passing the gate
only allows a human review, never statistical/causal pattern claims.
"""
import argparse
import importlib.util
import json
from pathlib import Path

spec=importlib.util.spec_from_file_location(
    "_igbd_account_state_for_review",Path(__file__).resolve().with_name("account_state.py"))
account=importlib.util.module_from_spec(spec)
spec.loader.exec_module(account)
FORMATS=account.FORMATS

def assess(data, config=None):
    if not isinstance(data,dict):
        raise ValueError("review data must be an object")
    fmt=data.get("format")
    if fmt not in FORMATS:
        raise ValueError("format must be an observed supported format")
    th=account.load_thresholds(config)
    bound=th["min_posts_for_baseline_by_format"].get(
        fmt,th["min_posts_for_baseline"])
    n=data.get("n_comparable_posts")
    reach=data.get("total_reach")
    if type(n) is not int or n<0 or type(reach) is not int or reach<0:
        raise ValueError("n_comparable_posts/total_reach must be explicit nonnegative integers")
    reasons=[]
    minimum=bound["value"]
    if n<minimum:
        reasons.append(f"{n} independent comparable posts < required N={minimum}")
    if reach==0:
        reasons.append("No positive-reach evidence")
    if data.get("verified_first_party") is not True:
        reasons.append("First-party data was not explicitly verified")
    if data.get("comparable") is not True:
        reasons.append("Comparable format, goal, observation window and context not confirmed")
    if data.get("account_state") in ("NO_DATA","DORMANT","ACTIVE_LOW_DATA"):
        reasons.append("Account state does not permit reliable active-performance baseline inference")
    if data.get("account_state") not in ("ACTIVE_WITH_BASELINE","NO_DATA","DORMANT","ACTIVE_LOW_DATA","COLD_START"):
        reasons.append("Validated account state is missing or unknown")
    return {
        "decision":"INSUFFICIENT_DATA" if reasons else "CANDIDATE_FOR_HUMAN_REVIEW",
        "reasons":reasons,
        "minimum_comparable_posts":minimum,
        "threshold_source":bound["source"],
        "format":fmt,
        "n_comparable_posts":n,
        "total_reach":reach,
        "learning_eligible":False,
        "executed":False,
        "note":"A threshold pass is not significance, causality or permission to write learnings.md."
    }

def main():
    p=argparse.ArgumentParser(description="Offline brand strategy sample gate")
    p.add_argument("input",type=Path)
    p.add_argument("--config",type=Path,help="Explicitly approved config.json only")
    args=p.parse_args()
    try:
        if args.config and args.config.name!="config.json":
            raise ValueError("Only approved config.json may set thresholds")
        data=json.loads(args.input.read_text(encoding="utf-8"))
        config=json.loads(args.config.read_text(encoding="utf-8")) if args.config else None
        result=assess(data,config)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0
    except (ValueError,OSError,TypeError) as e:
        print(json.dumps({"decision":"INVALID","error":str(e)},ensure_ascii=False))
        return 2

if __name__=="__main__":
    raise SystemExit(main())
