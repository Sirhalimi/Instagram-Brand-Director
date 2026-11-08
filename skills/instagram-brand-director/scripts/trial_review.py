#!/usr/bin/env python3
"""Conservative Trial Reel operational review (NOT proof of an algorithmic pattern).

Predeclared brand thresholds are editorial decision rules, not Meta guidance.
Individual posts never become learnings; repeat evidence is separately gated.
"""
import argparse
import json
import math
from pathlib import Path

METRICS = ("shares_per_reach", "likes_per_reach", "saves_per_reach", "follows_per_reach")
SOURCE = {"shares_per_reach": "shares", "likes_per_reach": "likes",
          "saves_per_reach": "saves", "follows_per_reach": "follows"}

def finite(x):
    return type(x) in (int, float) and math.isfinite(x) and x >= 0

def positive_int(x):
    return type(x) is int and x >= 1

def report(decision, reasons, **fields):
    return {"decision": decision, "reason": "; ".join(reasons), "evidence_gaps": reasons,
            "learning_eligible": False, "human_approval_required": True,
            "executed": False, **fields}

def review(trial, baseline, policy):
    if not all(isinstance(x, dict) for x in (trial, baseline, policy)):
        raise ValueError("trial, baseline and policy must be objects")
    if trial.get("trial_available") is False:
        return report("MANUAL_NORMAL_REEL", ["Trial is not enabled for this account"])
    if trial.get("is_trial") is not True:
        return report("HOLD", ["Post not confirmed as Trial Reel"])
    elapsed = trial.get("hours_since_publish")
    if not finite(elapsed):
        return report("INSUFFICIENT_DATA", ["Trial age missing or invalid"])
    minimum_hours = policy.get("minimum_elapsed_hours", 24)
    minimum_reach = policy.get("minimum_reach", 300)
    minimum_comparables = policy.get("minimum_comparable_posts", 6)
    minimum_baseline_reach = policy.get("minimum_baseline_reach", 1800)
    multiplier = policy.get("minimum_relative_to_baseline", 1.2)
    metric = policy.get("primary_metric", "shares_per_reach")
    if (not finite(minimum_hours) or minimum_hours <= 0 or
        not positive_int(minimum_reach) or not positive_int(minimum_comparables) or
        not positive_int(minimum_baseline_reach) or not finite(multiplier) or multiplier <= 0 or
        metric not in METRICS):
        raise ValueError("Invalid campaign sampling policy")
    if elapsed < minimum_hours:
        return report("WAIT_FOR_FIRST_REVIEW", ["Trial not mature for initial review"],
                      review_after_hours=minimum_hours)
    reasons = []
    reach = trial.get("reach")
    if not positive_int(reach) or reach < minimum_reach:
        reasons.append(f"Trial reach below brand minimum ({minimum_reach}) or missing")
    count = baseline.get("n_comparable_posts")
    if not positive_int(count) or count < minimum_comparables:
        reasons.append(f"Too few independent comparable baseline posts (need {minimum_comparables})")
    total = baseline.get("total_reach")
    if not positive_int(total) or total < minimum_baseline_reach:
        reasons.append(f"Insufficient pooled comparable baseline reach (need {minimum_baseline_reach})")
    if baseline.get("comparable") is not True:
        reasons.append("Baseline comparability (format, period, objective) not confirmed")
    value, base = trial.get(SOURCE[metric]), baseline.get(metric)
    if not finite(value) or not finite(base):
        reasons.append("Primary metric or baseline rate missing/invalid")
    if reasons:
        return report("INSUFFICIENT_DATA", reasons,
                      next_action="Collect more eligible samples; do not infer performance patterns or add learnings.",
                      review_after_hours=72 if elapsed < 72 else None)
    if base == 0:
        return report("INSUFFICIENT_DATA", ["Baseline rate is zero; relative lift is undefined"])
    observed_rate = value / reach
    relative = observed_rate / base
    if relative >= multiplier:
        decision = "RECOMMEND_SHARE_WITH_EVERYONE"
    elif elapsed < 72:
        decision = "KEEP_TRIAL_COLLECT_MORE_DATA"
    else:
        decision = "REWORK_NEXT_CREATIVE"
    return report(decision, ["Sufficient for an operational single-post comparison; NOT a learned repeatable pattern"],
                  metric=metric, observed_rate=round(observed_rate, 6),
                  account_baseline=base, observed_multiplier=round(relative, 3),
                  minimum_relative_to_baseline=multiplier,
                  review_after_hours=72 if decision=="KEEP_TRIAL_COLLECT_MORE_DATA" else None,
                  next_action="Human review; treat as a single observation only.",
                  inference="exploratory_single_post", minimum_reach=minimum_reach,
                  minimum_comparable_posts=minimum_comparables)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    args = parser.parse_args()
    data = json.loads(Path(args.input).read_text(encoding="utf8"))
    print(json.dumps(review(data["trial"], data["baseline"], data["policy"]), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
