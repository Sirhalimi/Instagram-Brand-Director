#!/usr/bin/env python3
"""Guardrail for recording repeatable learnings from multiple independent posts.

This tool never writes learnings.md. Passing the gate means candidate for a
human-approved observation, NOT proven causality or an algorithm discovery.
"""
import argparse, json
from pathlib import Path

def assess(experiments, policy=None):
    policy=policy or {}
    required=policy.get("min_independent_posts",4)
    minimum_reach=policy.get("min_reach_per_post",300)
    min_pooled_reach=policy.get("min_pooled_reach",3000)
    for v in (required,minimum_reach,min_pooled_reach):
        if type(v) is not int or v<1: raise ValueError("Sampling thresholds must be positive integers")
    if type(experiments) is not list:
        raise ValueError("experiments must be list")
    reasons=[]
    ids=[x.get("post_id") for x in experiments if isinstance(x,dict)]
    if len(ids)!=len(experiments) or any(not isinstance(x,str) or not x for x in ids) or len(ids)!=len(set(ids)):
        reasons.append("Need valid unique independent post IDs")
    if len(experiments)<required:
        reasons.append(f"Too few independent posts for a learning (need {required})")
    if any(type(x.get("reach")) is not int or x["reach"]<minimum_reach for x in experiments if isinstance(x,dict)):
        reasons.append(f"Every post must reach its predeclared minimum ({minimum_reach})")
    pooled=sum(x.get("reach",0) for x in experiments if isinstance(x,dict) and type(x.get("reach")) is int and x["reach"]>=0)
    if pooled<min_pooled_reach:
        reasons.append(f"Insufficient pooled sample (need {min_pooled_reach})")
    if any(x.get("comparable") is not True or x.get("data_verified") is not True for x in experiments if isinstance(x,dict)):
        reasons.append("Not all posts have verified comparable first-party data")
    if any(x.get("same_hypothesis") is not True for x in experiments if isinstance(x,dict)):
        reasons.append("Not all posts test the same predeclared hypothesis")
    if any(x.get("major_confounder") is not False for x in experiments if isinstance(x,dict)):
        reasons.append("Unresolved confounders")
    if reasons:
        return {"status":"INSUFFICIENT_DATA","reasons":reasons,"can_write_learnings":False,
                "allowed_record":"private_observations_only","pooled_reach":pooled}
    return {"status":"CANDIDATE_FOR_HUMAN_REVIEW",
            "reasons":["Repeatable observation is not causal proof; reviewer must verify strength and caveats"],
            "can_write_learnings":False,"allowed_record":"candidate_only",
            "pooled_reach":pooled,"independent_posts":len(experiments)}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("json_file",type=Path)
    a=ap.parse_args()
    data=json.loads(a.json_file.read_text(encoding="utf-8"))
    print(json.dumps(assess(data["experiments"],data.get("policy")),indent=2))
if __name__=="__main__":main()
