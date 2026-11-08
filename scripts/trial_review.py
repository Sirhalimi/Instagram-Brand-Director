#!/usr/bin/env python3
"""Post-Trial decision using account-specific baseline and business-defined policy.

Does not publish. Performance thresholds are not Instagram ranking rules.
"""
import argparse
import json
import math
from pathlib import Path

METRICS = ("shares_per_reach", "likes_per_reach", "saves_per_reach", "follows_per_reach")

def valid_nonnegative(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) and x >= 0

def review(trial, baseline, policy):
    if trial.get("trial_available") is False:
        return {"decision": "MANUAL_NORMAL_REEL", "reason": "Trial unavailable; do not claim it was tested."}
    if not trial.get("is_trial"):
        return {"decision": "HOLD", "reason": "Post is not identified as a Trial Reel."}
    elapsed = trial.get("hours_since_publish")
    if not valid_nonnegative(elapsed):
        return {"decision": "COLLECT_DATA", "reason": "Elapsed hours missing or invalid."}
    if elapsed < 24:
        return {"decision": "WAIT_FOR_FIRST_REVIEW", "reason": "Wait for approximately 24h initial measurement.", "review_after_hours": 24}
    if not valid_nonnegative(trial.get("reach")) or trial["reach"] == 0:
        return {"decision": "COLLECT_DATA", "reason": "No valid reach denominator."}
    minimum = policy.get("minimum_reach", 100)
    if not isinstance(minimum, int) or isinstance(minimum, bool) or minimum < 1:
        raise ValueError("minimum_reach must be a positive integer")
    if trial["reach"] < minimum:
        return {"decision": "KEEP_TRIAL_COLLECT_MORE_DATA" if elapsed < 72 else "ARCHIVE_OR_REWORK",
                "reason": "Account-specific minimum sample not reached; cannot compare reliably.",
                "review_after_hours": 72 if elapsed < 72 else None, "minimum_reach": minimum}
    metric = policy.get("primary_metric", "shares_per_reach")
    if metric not in METRICS:
        raise ValueError("Unsupported primary metric")
    source_key = {"shares_per_reach": "shares", "likes_per_reach": "likes",
                  "saves_per_reach": "saves", "follows_per_reach": "follows"}[metric]
    value = trial.get(source_key)
    base = baseline.get(metric)
    if not valid_nonnegative(value) or not valid_nonnegative(base):
        return {"decision": "COLLECT_DATA", "reason": "Selected metric/baseline missing; no comparison invented.", "metric": metric}
    rate = value / trial["reach"]
    uplift = rate / base if base > 0 else None
    multiplier = policy.get("minimum_relative_to_baseline", 1.0)
    if not valid_nonnegative(multiplier):
        raise ValueError("Invalid comparison multiplier")
    if base == 0:
        return {"decision": "MANUAL_REVIEW", "reason": "Historical baseline is zero; relative comparison undefined.", "observed_rate": round(rate, 6)}
    positive = uplift >= multiplier
    decision = "RECOMMEND_SHARE_WITH_EVERYONE" if positive else (
        "KEEP_TRIAL_COLLECT_MORE_DATA" if elapsed < 72 else "REWORK_NEXT_CREATIVE")
    return {"decision": decision, "metric": metric, "observed_rate": round(rate, 6),
            "account_baseline": base, "observed_multiplier": round(uplift, 3),
            "minimum_relative_to_baseline": multiplier,
            "reason": ("Meets" if positive else "Below") + " brand-configured performance criterion.",
            "review_after_hours": None if positive or elapsed >= 72 else 72,
            "human_approval_required": True, "executed": False,
            "notice": "Not an Instagram algorithm rule or causal estimate. Check comparability and business outcomes."}

def main():
    parser = argparse.ArgumentParser(description="Review Trial Reel against account baseline")
    parser.add_argument("input", help="JSON with trial, baseline and policy")
    args = parser.parse_args()
    data = json.loads(Path(args.input).read_text(encoding="utf8"))
    print(json.dumps(review(data["trial"], data["baseline"], data["policy"]), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
