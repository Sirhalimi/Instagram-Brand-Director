#!/usr/bin/env python3
"""Build an auditable, pooled baseline candidate from validated first-party CSV.

Never labels historical posts comparable automatically. Does not write without
an explicitly requested output path; no Instagram/account/network access.
"""
import argparse
import csv
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import importlib.util

# Resolve the validator from this installed Skill, not from any unrelated
# top-level `scripts` Python package in the host repository/agent environment.
_validator_path = Path(__file__).resolve().with_name('validate_data.py')
_spec = importlib.util.spec_from_file_location('_igbd_validator', _validator_path)
_validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_validator)
read_md = _validator.read_md
validate_brand = _validator.validate_brand
validate_posts_csv = _validator.validate_posts_csv
validate_baseline = _validator.validate_baseline

METRICS = ("likes", "shares", "saves", "follows")
FORMATS = ("reel", "carousel", "story", "image")

def compile_baseline(brand, csv_text, *, as_of, start, target_format="reel",
                     goal=None, target_age_hours=72, tolerance_hours=12,
                     min_posts=6, min_pooled_reach=1800,
                     human_reviewed_comparability=False):
    errors = validate_brand(brand)
    csv_errors, _ = validate_posts_csv(csv_text)
    if errors or csv_errors:
        raise ValueError("Invalid input; no baseline computed: " + "; ".join(errors + csv_errors))
    if type(as_of) is not date or type(start) is not date or start > as_of:
        raise ValueError("Use valid increasing observation date window")
    if target_format not in FORMATS:
        raise ValueError("Unknown format")
    goal = goal or brand["primary_goal"]
    if goal not in ("discovery","community","conversion","education"):
        raise ValueError("Unknown campaign goal")
    for name, x in [("target_age_hours",target_age_hours),("tolerance_hours",tolerance_hours),
                    ("min_posts",min_posts),("min_pooled_reach",min_pooled_reach)]:
        if type(x) is not int or x < (0 if name == "tolerance_hours" else 1):
            raise ValueError(f"Invalid positive sampling policy: {name}")
    included=[]
    for row in csv.DictReader(csv_text.splitlines()):
        # Trial data is excluded from organic historical baseline.
        if row["format"] != target_format or row["goal"] != goal or row.get("trial") == "true":
            continue
        date_local = datetime.fromisoformat(row["published_at"].replace("Z","+00:00")).date()
        if not start <= date_local <= as_of:
            continue
        src=row["source"].strip().lower()
        if src in ("example_only","not_collected","demo","sample","synthetic"):
            raise ValueError("Sample/demo data cannot be promoted to an evidence baseline")
        included.append(row)
    pooled_reach = sum(int(row["reach"]) for row in included)
    count = len(included)
    all_windows = all(row.get("metrics_age_hours","").strip() and
                      abs(int(row["metrics_age_hours"]) - target_age_hours) <= tolerance_hours
                      for row in included)
    reasons=[]
    if count < min_posts:
        reasons.append(f"Only {count} independent eligible posts; minimum is {min_posts}")
    if pooled_reach < min_pooled_reach:
        reasons.append(f"Pooled reach {pooled_reach} < minimum {min_pooled_reach}")
    if not all_windows:
        reasons.append("Post metric observation ages absent or outside comparable window")
    if not human_reviewed_comparability:
        reasons.append("Human has not verified comparable creative/audience context")
    if pooled_reach == 0:
        reasons.append("No reach denominator")
    ratios = {k+"_per_reach": (round(sum(int(x[k]) for x in included)/pooled_reach, 9)
                              if pooled_reach else 0.0) for k in METRICS}
    baseline={
        "schema_version":1,
        "brand_id":brand["brand_id"],
        "as_of":as_of.isoformat(),
        "window_start":start.isoformat(),
        "format":target_format,
        "primary_goal":goal,
        "n_comparable_posts":count,
        "total_reach":pooled_reach,
        "comparable":not reasons,
        "source":"validated_posts_csv:" + ",".join(sorted({row["source"] for row in included})) if included else "NO_ELIGIBLE_POSTS",
        "status":"READY_FOR_OPERATIONAL_COMPARISON" if not reasons else "INSUFFICIENT_DATA",
        "evidence_gaps":reasons,
        "target_metrics_age_hours":target_age_hours,
        "observation_tolerance_hours":tolerance_hours,
        "post_ids":[x["post_id"] for x in included],
        **ratios
    }
    check=validate_baseline(baseline)
    if check:
        raise AssertionError("Generated baseline violates own contract: "+"; ".join(check))
    return baseline

def main():
    ap=argparse.ArgumentParser(description="Audit first-party comparable-post baseline")
    ap.add_argument("--brand",required=True,type=Path)
    ap.add_argument("--posts",required=True,type=Path)
    ap.add_argument("--as-of",required=True,type=date.fromisoformat)
    ap.add_argument("--start",required=True,type=date.fromisoformat)
    ap.add_argument("--format",choices=FORMATS,default="reel")
    ap.add_argument("--goal",choices=("discovery","community","conversion","education"))
    ap.add_argument("--observation-hours",type=int,default=72)
    ap.add_argument("--tolerance-hours",type=int,default=12)
    ap.add_argument("--reviewed-comparability",action="store_true",
                    help="Manual assertion AFTER checking that posts truly share comparable context")
    ap.add_argument("--output",type=Path,help="Optional private baseline.md output; refuses overwrite")
    args=ap.parse_args()
    d=compile_baseline(read_md(args.brand),args.posts.read_text(encoding="utf-8-sig"),
        as_of=args.as_of,start=args.start,target_format=args.format,goal=args.goal,
        target_age_hours=args.observation_hours,tolerance_hours=args.tolerance_hours,
        human_reviewed_comparability=args.reviewed_comparability)
    print(json.dumps(d,indent=2,ensure_ascii=False))
    if args.output:
        text="# Instagram baseline — generated from provided first-party posts\n\n"+ "\u0060"*3+"json\n"+json.dumps(d,indent=2,ensure_ascii=False)+"\n"+"\u0060"*3+"\n"
        with args.output.open("x",encoding="utf-8") as f:
            f.write(text)
if __name__=="__main__":
    main()
