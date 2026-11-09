#!/usr/bin/env python3
"""Deterministic Instagram account-state classification, no network or secrets.

All DEFAULT_THRESHOLDS are *uncalibrated editorial assumptions*, NOT Meta
eligibility requirements or Instagram algorithm rules. Missing != zero.
Only reads a supplied input file and a supplied or same-directory config.json.
"""
import argparse
import json
import math
from datetime import date, timedelta
from pathlib import Path
from statistics import median

DEFAULT_THRESHOLDS = {
    "cold_start_max_followers": 50,
    "cold_start_max_posts": 5,
    "dormant_after_days": 60,
    "min_posts_for_baseline": 12,
    "baseline_window_days": 90,
    "has_audience_min_followers": 200,
}
FORMATS = {"reel", "carousel", "story", "image", "video", "static"}
RATES = {
    "sends_per_reach": "sends",
    "likes_per_reach": "likes",
    "saves_per_reach": "saves",
    "follows_per_reach": "follows_gained",
}
STATES = {"NO_DATA", "COLD_START", "DORMANT",
          "ACTIVE_LOW_DATA", "ACTIVE_WITH_BASELINE"}

def _count(value):
    return type(value) is int and value >= 0

def _date(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = date.fromisoformat(value)
        return parsed if parsed.isoformat() == value else None
    except ValueError:
        return None

def _number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0

def _med_mad(samples):
    med = median(samples)
    return {"median": round(float(med), 9),
            "mad": round(float(median([abs(x - med) for x in samples])), 9),
            "n": len(samples)}

def load_thresholds(config=None):
    """Support the calibrated config format while never silently accepting bad data.

    Source values always have a recorded default/derived provenance.
    Per-format overrides live at thresholds.min_posts_for_baseline_by_format.
    """
    if config is not None and not isinstance(config, dict):
        raise ValueError("config must be an object")
    rows = (config or {}).get("thresholds", {})
    if not isinstance(rows, dict):
        raise ValueError("config.thresholds must be an object")
    result = {}
    for key, default in DEFAULT_THRESHOLDS.items():
        value = rows.get(key)
        if value is None:
            result[key] = {"value": default, "source": "default"}
            continue
        if not isinstance(value, dict) or "value" not in value:
            raise ValueError("threshold %s must contain value and source" % key)
        n, source = value["value"], value.get("source")
        if not _count(n) or n < 1 or source not in ("default", "derived"):
            # Zero is meaningful for cold-start follower/post floors only.
            if not (key in ("cold_start_max_followers", "cold_start_max_posts")
                    and n == 0 and type(n) is int and source in ("default", "derived")):
                raise ValueError("invalid threshold %s" % key)
        if source == "derived" and not value.get("evidence"):
            raise ValueError("derived threshold %s has no evidence" % key)
        result[key] = {"value": n, "source": source}
    formats = rows.get("min_posts_for_baseline_by_format", {})
    if not isinstance(formats, dict):
        raise ValueError("per-format thresholds must be an object")
    result["min_posts_for_baseline_by_format"] = {}
    for fmt, obj in formats.items():
        if fmt not in FORMATS or not isinstance(obj, dict):
            raise ValueError("invalid per-format threshold")
        n, source = obj.get("value"), obj.get("source")
        if not _count(n) or n < 2 or source not in ("derived", "default"):
            raise ValueError("invalid min_posts_for_baseline by format")
        if source == "derived" and not obj.get("evidence"):
            raise ValueError("derived per-format threshold missing evidence")
        result["min_posts_for_baseline_by_format"][fmt] = {
            "value": n, "source": source
        }
    return result

def _trial_eligibility(data, followers, restricted):
    toggle = data.get("trial_toggle_seen_in_app", "unknown")
    if toggle not in (True, False, "unknown", None):
        raise ValueError("trial_toggle_seen_in_app must be boolean or unknown")
    if restricted is True:
        return "no", ["Account Status reports recommendation ineligibility"]
    if followers is None:
        return "unknown", ["Follower count unavailable"]
    if followers < 200:
        return "no", ["Below 200 followers; conservative rule pending official-source resolution"]
    if toggle is True:
        return "yes", ["Trial toggle observed in the native app; verify each post's actual status"]
    if followers < 1000:
        return "unknown", ["200–999 follower eligibility sources conflict; check native Trial toggle"]
    return "unknown", ["1,000+ followers does not prove eligibility; verify Trial in app and Account Status"]

def _ghost(data, config, state, followers, recent):
    """Risk requires self-history. No population 'ghost percentage' is inferred."""
    evidence, notes = [], []
    confidence = "low"
    sample = data.get("manual_follower_sample")
    pct = None
    if sample is not None:
        if not isinstance(sample, dict) or not _count(sample.get("n")) or not _count(sample.get("suspicious_n")):
            raise ValueError("manual_follower_sample needs nonnegative n/suspicious_n")
        n, suspicious = sample["n"], sample["suspicious_n"]
        if suspicious > n:
            raise ValueError("suspicious_n cannot exceed n")
        if n < 30:
            notes.append("Manual sample n<30: too small to generalize; no percentage estimate")
        else:
            pct = round(100.0 * suspicious / n, 1)
            evidence.append("Human-labeled sample: %d suspicious in %d reviewed followers (%.1f%% of SAMPLE only)" %
                            (suspicious, n, pct))
    spike = data.get("follower_growth_spike_flag", "unknown")
    if spike not in (True, False, None, "unknown"):
        raise ValueError("follower_growth_spike_flag invalid")
    if spike is True:
        evidence.append("Unexplained follower growth spike was explicitly reported")
    aud = data.get("audience", {})
    if aud is None:
        aud = {}
    if not isinstance(aud, dict):
        raise ValueError("audience must be an object")
    top, target = aud.get("top_countries"), aud.get("target_countries")
    if isinstance(top, list) and isinstance(target, list) and top and target:
        named = {x.get("country") for x in top if isinstance(x, dict)}
        if named.isdisjoint(set(x for x in target if isinstance(x, str))):
            evidence.append("Target countries absent from the supplied top-country sample; not proof of fake followers")
    prior = (config or {}).get("ghost_self_baseline", {})
    if not isinstance(prior, dict) or prior.get("status") != "available":
        notes.append("No earlier verified active-period self-baseline; ghost_risk stays unknown")
        return {"level": "unknown", "confidence": "low", "evidence": evidence,
                "notes": notes, "sample_suspicious_pct": pct}
    if state == "DORMANT":
        notes.append("Dormant reach ratios are confounded; reactivation window required before a ghost judgment")
        return {"level": "unknown", "confidence": "low", "evidence": evidence,
                "notes": notes, "sample_suspicious_pct": pct}
    prior_reach = prior.get("reach_per_follower")
    if not isinstance(prior_reach, dict) or not _number(prior_reach.get("median")):
        notes.append("Self-baseline lacks a valid reach/follower median")
        return {"level": "unknown", "confidence": "low", "evidence": evidence,
                "notes": notes, "sample_suspicious_pct": pct}
    current_ratios = ([p["reach"] / followers for p in recent
                       if followers and _number(p.get("reach")) and p["reach"] > 0])
    if len(current_ratios) < 3:
        notes.append("Fewer than three recent comparable reach observations")
        return {"level": "unknown", "confidence": "low", "evidence": evidence,
                "notes": notes, "sample_suspicious_pct": pct}
    old_median, old_mad = prior_reach["median"], prior_reach.get("mad")
    if not _number(old_mad):
        notes.append("Self-baseline spread missing")
        return {"level": "unknown", "confidence": "low", "evidence": evidence,
                "notes": notes, "sample_suspicious_pct": pct}
    current = median(current_ratios)
    # A deviation is only compared to this brand's own historical median/MAD;
    # this is a heuristic, not a universal "healthy engagement" cut-off.
    if current < old_median - 2 * old_mad and old_median > 0:
        evidence.append("Recent reach/follower median below this brand's own earlier median by >2 prior MADs")
        reach_decline = True
    else:
        evidence.append("Recent reach/follower median is not below the prior self-history MAD band")
        reach_decline = False
    count_signals = int(reach_decline)
    past_story = prior.get("story_views_per_follower")
    current_story = data.get("story_views_median")
    if isinstance(past_story, dict) and _number(past_story.get("median")) and \
       _number(past_story.get("mad")) and _count(current_story) and followers > 0:
        if current_story / followers < past_story["median"] - 2 * past_story["mad"]:
            count_signals += 1
            evidence.append("Story view/follower rate fell below own historical MAD band")
    if spike is True:
        count_signals += 1
    level = "high" if count_signals >= 2 else "medium" if count_signals == 1 else "low"
    confidence = "medium" if len(current_ratios) >= 5 else "low"
    return {"level": level, "confidence": confidence, "evidence": evidence,
            "notes": notes, "sample_suspicious_pct": pct}

def classify(data, config=None):
    if not isinstance(data, dict):
        raise ValueError("account input must be an object")
    thresholds = load_thresholds(config)
    today = _date(data.get("today")) if "today" in data else date.today()
    if today is None:
        raise ValueError("today must be ISO YYYY-MM-DD")
    followers = data.get("followers")
    missing = []
    if not _count(followers):
        missing.append("followers")
        followers = None
    raw = data.get("posts")
    if not isinstance(raw, list):
        missing.append("posts")
        raw = []
    posts, bad_dates = [], False
    for item in raw:
        if not isinstance(item, dict) or _date(item.get("date")) is None:
            bad_dates = True
            continue
        if _date(item["date"]) > today:
            bad_dates = True
            continue
        posts.append({**item, "_date": _date(item["date"])})
    if bad_dates:
        missing.append("posts[].date")
    span = thresholds["baseline_window_days"]["value"]
    recent = [p for p in posts if p["_date"] >= today - timedelta(days=span)]
    state, reasons = "NO_DATA", []
    if missing:
        reasons.append("State-critical data missing or invalid: " + ", ".join(missing))
    else:
        last = max((p["_date"] for p in posts), default=None)
        dormant_days = thresholds["dormant_after_days"]["value"]
        if last is not None and (today - last).days > dormant_days:
            state = "DORMANT"
            reasons.append("Last recorded post older than %d days" % dormant_days)
        elif (followers <= thresholds["cold_start_max_followers"]["value"] and
              len(recent) <= thresholds["cold_start_max_posts"]["value"]):
            state = "COLD_START"
            reasons.append("Follower count and recent post count meet uncalibrated cold-start thresholds")
        else:
            state = "ACTIVE_LOW_DATA"
    baseline = None
    if state == "ACTIVE_LOW_DATA":
        by_format = {}
        for p in recent:
            if p.get("format") not in FORMATS or not _count(p.get("reach")) or p["reach"] <= 0:
                continue
            by_format.setdefault(p["format"], []).append(p)
        output = {}
        for fmt, records in sorted(by_format.items()):
            rule = thresholds["min_posts_for_baseline_by_format"].get(
                fmt, thresholds["min_posts_for_baseline"])
            minimum = rule["value"]
            if len(records) < minimum:
                continue
            rates = {}
            for metric, count_key in RATES.items():
                vals = [p[count_key] / p["reach"] for p in records
                        if _count(p.get(count_key))]
                if len(vals) >= minimum:
                    rates[metric] = _med_mad(vals)
            if rates:
                output[fmt] = {
                    "n_posts_with_reach": len(records),
                    "baseline_min_posts": minimum,
                    "reach": _med_mad([p["reach"] for p in records]),
                    "rates": rates,
                    "window_days": span,
                }
        if output:
            state = "ACTIVE_WITH_BASELINE"
            baseline = output
            reasons.append("At least one format has enough independent reach-denominated observations")
        else:
            reasons.append("Not enough comparable positive-reach posts with nonmissing metric data")
            if any("reach" not in p for p in recent):
                missing.append("posts[].reach")
    if state == "DORMANT":
        reasons.append("Do not use stale historical engagement as an active baseline")
    status = data.get("account_status", {})
    if status is None:
        status = {}
    if not isinstance(status, dict):
        raise ValueError("account_status must be an object")
    eligible = status.get("eligible_for_recommendations", "unknown")
    if eligible not in (True, False, None, "unknown"):
        raise ValueError("recommendation eligibility must be boolean or unknown")
    restricted = True if eligible is False else False if eligible is True else "unknown"
    trial, trial_notes = _trial_eligibility(data, followers, restricted)
    ghost = _ghost(data, config, state, followers, recent)
    has_audience = ("unknown" if followers is None else
                    followers >= thresholds["has_audience_min_followers"]["value"])
    flags = {
        "ghost_risk": ghost["level"],
        "ghost_risk_confidence": ghost["confidence"],
        "ghost_risk_evidence": ghost["evidence"],
        "ghost_risk_notes": ghost["notes"],
        "originality_risk": "unknown",
        "originality_notes": ["No independently verified content originality or rights evidence supplied"],
        "restricted": restricted,
        "trial_eligible": trial,
        "trial_notes": trial_notes,
        "has_audience": has_audience,
    }
    if ghost["sample_suspicious_pct"] is not None:
        flags["sample_suspicious_pct"] = ghost["sample_suspicious_pct"]
        flags["sample_percentage_scope"] = "reviewed manual sample only; no population estimate"
    profiles = {
        "NO_DATA": ("request_data", ["REQUEST_CRITICAL_DATA"], "Request followers and dated post history"),
        "COLD_START": ("cold_start_discovery", ["NORMAL_REEL", "BUILD_INITIAL_BASELINE"],
                       "HYPOTHESIS: original discovery content; gather first-party reach evidence"),
        "DORMANT": ("reactivation_measurement", ["RUN_REACTIVATION_WINDOW"],
                    "Resume a measurable posting window before diagnosing followers"),
        "ACTIVE_LOW_DATA": ("baseline_collection", ["COLLECT_COMPARABLE_POSTS"],
                            "Gather enough same-format posts with positive reach and metric counts"),
        "ACTIVE_WITH_BASELINE": ("own_baseline_strategy", ["COMPARE_TO_OWN_FORMAT_BASELINE"],
                                 "Use per-format medians and MAD with measurement windows"),
    }
    profile, next_actions, approach = profiles[state]
    confidence = "low" if state == "NO_DATA" else "medium" if state == "ACTIVE_LOW_DATA" else "high"
    return {
        "state": state, "confidence": confidence, "flags": flags,
        "reasons": reasons, "missing_data": sorted(set(missing)),
        "baseline": baseline, "thresholds_used": thresholds,
        "next_action_codes": next_actions,
        "strategy_profile": {"id": profile, "approach": approach,
                             "hypothesis_not_platform_fact": True},
    }

def main():
    parser = argparse.ArgumentParser(description="Classify account state from explicitly supplied data")
    parser.add_argument("input", type=Path)
    parser.add_argument("--config", type=Path, help="Optional approved config.json")
    args = parser.parse_args()
    account = json.loads(args.input.read_text(encoding="utf-8"))
    config_path = args.config
    if config_path is None:
        sibling = args.input.parent / "config.json"
        if sibling.is_file():
            config_path = sibling
    config = json.loads(config_path.read_text(encoding="utf-8")) if config_path else None
    print(json.dumps(classify(account, config), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
