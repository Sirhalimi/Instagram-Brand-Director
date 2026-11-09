#!/usr/bin/env python3
"""Propose auditable brand-specific thresholds from the brand's own CSV history.

No experiments, network, API tokens or external paths are used. Reads only
explicit supplied files. Never overwrites config.json or a prior proposal.
Every derivation is an observational HEURISTIC, not an Instagram rule.
"""
import argparse
import csv
import difflib
import io
import json
import math
from datetime import date
from pathlib import Path
from statistics import median

# Resolve sibling module by path so standalone installed Skill scripts work
# even when the embedding project's import path has a different scripts package.
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "_igbd_account_state", Path(__file__).resolve().with_name("account_state.py"))
_account = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_account)
DEFAULT_THRESHOLDS = _account.DEFAULT_THRESHOLDS
_med_mad = _account._med_mad
_date = _account._date

REQUIRED_COLUMNS = (
    "date", "format", "topic", "hook", "duration_s", "trial", "reach",
    "non_follower_share", "watch_time", "sends", "saves", "likes", "follows_gained"
)
COUNT_COLUMNS = ("reach", "sends", "saves", "likes", "follows_gained")
RATE_COLUMNS = ("sends", "saves", "likes", "follows_gained")
VALID_FORMATS = ("reel", "carousel", "story", "image", "video", "static")
VALID_SETTINGS = {
    "stability_percent": 0.10,
    "stability_consecutive_steps": 3,
    "minimum_candidate_posts": 6,
    "earlier_period_min_posts": 5,
}

def _integer(value):
    if value is None or value == "":
        return None
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    raise ValueError("Expected nonnegative integer or missing: %r" % value)

def _finite_nonnegative(raw):
    if raw is None or raw == "":
        return None
    try:
        val = float(raw)
        if math.isfinite(val) and val >= 0:
            return val
    except (ValueError, TypeError):
        pass
    raise ValueError("Invalid nonnegative number: %r" % raw)

def parse_posts_csv(text):
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or set(REQUIRED_COLUMNS) - set(reader.fieldnames):
        raise ValueError("CSV missing columns: " +
                         ", ".join(sorted(set(REQUIRED_COLUMNS) - set(reader.fieldnames or []))))
    if len(reader.fieldnames) != len(set(reader.fieldnames)):
        raise ValueError("Duplicate columns")
    rows = []
    for line_no, row in enumerate(reader, 2):
        when = _date(row.get("date"))
        if when is None:
            raise ValueError("Row %d: date must be YYYY-MM-DD" % line_no)
        fmt = row.get("format")
        if fmt not in VALID_FORMATS:
            raise ValueError("Row %d: invalid format" % line_no)
        if row.get("trial") not in ("true", "false", ""):
            raise ValueError("Row %d: trial must be true, false or empty" % line_no)
        item = dict(row)
        item["_date"] = when
        for key in COUNT_COLUMNS:
            item[key] = _integer(row.get(key))
        for key in ("non_follower_share", "watch_time", "duration_s"):
            item[key] = _finite_nonnegative(row.get(key))
        if item["non_follower_share"] is not None and item["non_follower_share"] > 1:
            raise ValueError("Row %d: non_follower_share must be a fraction" % line_no)
        rows.append(item)
    return sorted(rows, key=lambda p: p["_date"])

def _default(value, reason):
    return {"value": value, "source": "default", "confidence": "low",
            "evidence": {"status": "insufficient_data", "reason": reason,
                         "notice": "Default is an uncalibrated assumption, not Instagram policy"}}

def _derived(value, evidence, confidence="medium"):
    return {"value": value, "source": "derived", "confidence": confidence,
            "evidence": {"status": "derived", **evidence,
                         "notice": "Brand-specific observational heuristic, not Meta policy"}}

def _settings(settings):
    options = dict(VALID_SETTINGS)
    if settings is not None:
        if not isinstance(settings, dict):
            raise ValueError("calibration settings must be an object")
        extra = set(settings) - set(options)
        if extra:
            raise ValueError("Unrecognized calibration settings: " + ", ".join(sorted(extra)))
        options.update(settings)
    p, steps, min_n, earlier = (options[x] for x in
        ("stability_percent", "stability_consecutive_steps",
         "minimum_candidate_posts", "earlier_period_min_posts"))
    if type(p) not in (float, int) or not math.isfinite(p) or not 0 < p <= 1:
        raise ValueError("stability_percent must be finite between 0 and 1")
    if any(type(v) is not int or v < 1 for v in (steps, min_n, earlier)):
        raise ValueError("sample sizes and stability steps must be positive integers")
    return options

def derive_min_posts(records, *, options):
    """Smallest stable chronological prefix for four per-reach medians.

    N must remain stable for multiple further posts. A flat one-step median
    or a four-metric all-zero sequence is insufficient evidence.
    """
    usable = [p for p in records if p["reach"] and p["reach"] > 0 and
              all(p[k] is not None for k in RATE_COLUMNS)]
    threshold = options["stability_percent"]
    steps = options["stability_consecutive_steps"]
    min_n = options["minimum_candidate_posts"]
    if len(usable) < min_n + steps:
        return _default(DEFAULT_THRESHOLDS["min_posts_for_baseline"],
                        "insufficient data for median stability: %d usable posts" % len(usable))
    rates = {k: [p[k] / p["reach"] for p in usable] for k in RATE_COLUMNS}
    if not any(any(x > 0 for x in seq) for seq in rates.values()):
        return _default(DEFAULT_THRESHOLDS["min_posts_for_baseline"],
                        "baseline unstable: all event rates are zero, no signal")
    medians = {k: [median(values[:n]) for n in range(1, len(usable) + 1)]
               for k, values in rates.items()}
    for n in range(min_n, len(usable) - steps + 1):
        stable = True
        for seq in medians.values():
            for index in range(n - 1, n - 1 + steps):
                old, new = seq[index], seq[index + 1]
                if old == new:
                    continue
                if old == 0 or abs(new - old) / abs(old) > threshold:
                    stable = False
                    break
            if not stable:
                break
        if stable:
            return _derived(n, {
                "method": "smallest stable prefix of consecutive median changes",
                "format_n": len(usable), "stability_percent": threshold,
                "consecutive_steps": steps, "minimum_candidate_posts": min_n,
                "metrics": list(RATE_COLUMNS), "first_post": usable[0]["date"],
                "last_post": usable[-1]["date"]})
    return _default(DEFAULT_THRESHOLDS["min_posts_for_baseline"],
                    "baseline unstable: no N passed every metric and consecutive step")

def derive_ghost_self_baseline(rows, growth, options):
    """Needs explicitly supplied prior active period and historical denominator."""
    result = {"status": "insufficient_data", "source": "default",
              "ghost_risk": "unknown",
              "reason": "No earlier active-period post reach and matching follower history",
              "confidence": "low"}
    if not isinstance(growth, dict):
        return result
    period = growth.get("earlier_active_period")
    if not isinstance(period, dict):
        return result
    start, end = _date(period.get("start")), _date(period.get("end"))
    followers = period.get("followers")
    if start is None or end is None or end < start or type(followers) is not int or followers <= 0:
        return result
    eligible = [p for p in rows if start <= p["_date"] <= end and
                p["reach"] is not None and p["reach"] > 0 and p.get("trial") != "true"]
    if len(eligible) < options["earlier_period_min_posts"]:
        result["reason"] = "Insufficient earlier active-period reach samples"
        return result
    ratios = [p["reach"] / followers for p in eligible]
    result = {"status": "available", "source": "derived", "confidence": "medium",
              "ghost_risk": "unknown",
              "reach_per_follower": _med_mad(ratios),
              "n_earlier_posts": len(eligible),
              "evidence": {"earlier_active_period": {"start": start.isoformat(),
                         "end": end.isoformat(), "followers": followers},
                           "post_dates": [p["date"] for p in eligible],
                           "denominator_note": "Historic follower count is supplied, not inferred",
                           "method": "earlier reach / prior followers median and MAD"}}
    story = period.get("story_views_median")
    if type(story) is int and story >= 0:
        result["story_views_per_follower"] = {
            "median": round(story / followers, 9), "mad": None, "n": None,
            "note": "Single earlier aggregate cannot yield dispersion"}
    return result

def calibrate(rows, *, audience=None, growth=None, settings=None, today=None):
    if not isinstance(rows, list):
        raise ValueError("rows must be a list")
    options = _settings(settings)
    as_of = today or date.today()
    if type(as_of) is not date:
        raise ValueError("today must be a date object")
    posts = [p for p in rows if p["_date"] <= as_of]
    thresholds = {k: _default(v, "No brand-specific method/evidence for this threshold")
                  for k, v in DEFAULT_THRESHOLDS.items()}
    # The follower/cold-start floors and baseline window cannot be calibrated
    # from this CSV. They remain explicitly uncalibrated defaults.
    if len(posts) >= 5:
        dates = sorted(p["_date"] for p in posts)
        gaps = [(b - a).days for a, b in zip(dates, dates[1:])]
        value = max(30, math.ceil(4 * median(gaps)))
        thresholds["dormant_after_days"] = _derived(
            value, {"method": "max(30, ceil(4 * median posting gap))",
                    "posts": len(posts), "median_gap_days": float(median(gaps)),
                    "start": dates[0].isoformat(), "end": dates[-1].isoformat()})
    else:
        thresholds["dormant_after_days"] = _default(
            DEFAULT_THRESHOLDS["dormant_after_days"], "insufficient data: fewer than 5 posts")
    by_format = {}
    for fmt in VALID_FORMATS:
        sub = [p for p in posts if p["format"] == fmt and p["trial"] != "true"]
        by_format[fmt] = derive_min_posts(sub, options=options)
    thresholds["min_posts_for_baseline_by_format"] = by_format
    ghost = derive_ghost_self_baseline(posts, growth, options)
    return {
        "schema_version": 1, "proposed_on": as_of.isoformat(),
        "approval_status": "proposed_not_active",
        "methodology": "Brand-specific observational HEURISTICS, not Instagram rules",
        "thresholds": thresholds, "ghost_self_baseline": ghost,
        "audience_context": {
            "provided": audience is not None,
            "note": "Audience geography alone cannot derive fake/ghost follower percentages"},
    }

def make_diff(old, proposed):
    before = json.dumps(old, indent=2, sort_keys=True, ensure_ascii=False).splitlines(True)
    after = json.dumps(proposed, indent=2, sort_keys=True, ensure_ascii=False).splitlines(True)
    return "".join(difflib.unified_diff(before, after, fromfile="approved/config.json",
                                        tofile="proposed/config.proposed.json"))

def propose(posts_path, *, config_path=None, output_path=None, audience_path=None,
            growth_path=None, settings=None, today=None):
    """Safely create a proposed config, never overwrite an approved config."""
    p = Path(posts_path)
    rows = parse_posts_csv(p.read_text(encoding="utf-8-sig"))
    old_path = Path(config_path) if config_path is not None else p.parent / "config.json"
    existing = json.loads(old_path.read_text(encoding="utf-8")) if old_path.exists() else {
        "schema_version": 1,
        "thresholds": {k: {"value": v, "source": "default"}
                       for k, v in DEFAULT_THRESHOLDS.items()}}
    audience = json.loads(Path(audience_path).read_text(encoding="utf-8")) if audience_path else None
    growth = json.loads(Path(growth_path).read_text(encoding="utf-8")) if growth_path else None
    result = calibrate(rows, audience=audience, growth=growth, settings=settings, today=today)
    out = Path(output_path) if output_path is not None else p.parent / "config.proposed.json"
    if out.resolve() == old_path.resolve() or out.name == "config.json":
        raise ValueError("Refusing to overwrite approved config.json")
    with out.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return {"proposed_path": str(out), "approved_config_unchanged": True,
            "proposal": result, "diff": make_diff(existing, result)}

def main():
    ap = argparse.ArgumentParser(description="Propose brand-specific thresholds; no auto-approval")
    ap.add_argument("posts", type=Path)
    ap.add_argument("--config", type=Path, help="Existing approved config to diff; never write")
    ap.add_argument("--output", type=Path, help="Explicit proposed config path")
    ap.add_argument("--audience", type=Path, help="Optional audience JSON")
    ap.add_argument("--growth", type=Path, help="Optional growth / earlier period JSON")
    ap.add_argument("--today", type=date.fromisoformat)
    ap.add_argument("--stability-percent", type=float, default=0.10)
    ap.add_argument("--stable-steps", type=int, default=3)
    ap.add_argument("--minimum-candidate-posts", type=int, default=6)
    args = ap.parse_args()
    outcome = propose(args.posts, config_path=args.config, output_path=args.output,
        audience_path=args.audience, growth_path=args.growth, today=args.today,
        settings={"stability_percent": args.stability_percent,
                  "stability_consecutive_steps": args.stable_steps,
                  "minimum_candidate_posts": args.minimum_candidate_posts})
    print(json.dumps({"proposed_path": outcome["proposed_path"],
                      "approved_config_unchanged": True}, indent=2))
    print(outcome["diff"])

if __name__ == "__main__":
    main()
