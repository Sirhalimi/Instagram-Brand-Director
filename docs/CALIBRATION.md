# Data-derived calibration and approval

All calibrations use the brand's own records. No script connects to Instagram, requests credentials, publishes, or modifies a production config. Defaults are explicitly **uncalibrated assumptions**, not Instagram rules.

## Inputs and schema distinction
The new calibration CSV requires columns:
date, format, topic, hook, duration_s, trial, reach, non_follower_share, watch_time, sends, saves, likes, follows_gained.

Empty values mean **missing**, never zero. date is ISO YYYY-MM-DD; reach and counts are nonnegative integers when present, trial is true/false/empty. The older validated analytics posts.csv format uses post_id/published_at/goal/source and is DIFFERENT. The conversion between these schemas is **not implemented** in Phase 1; do not silently substitute one format for the other.

Optional --growth points to JSON that contains earlier_active_period: {start, end, followers, story_views_median}. It must refer to the past **active** period, use historical followers rather than today's denominator, and contain >=5 earlier positive-reach posts for self-comparison. Optional --audience points to a supplied JSON, used for context only (not a fake-follower estimate). All paths must be explicitly supplied or beside the supplied CSV.

## CLI (synthetic sample, never a real brand)
python3 -m scripts.calibrate_thresholds examples/calibration.wholesale.posts.sample.csv --growth examples/calibration.wholesale.growth.sample.json --today 2026-11-09 --output /tmp/config.proposed.json

The command creates only the proposed file with exclusive creation mode. If there is an approved config.json, it remains byte-for-byte unchanged. The console prints a unified diff against the approved config or documented defaults. Never interpret creating config.proposed.json as owner approval; after reviewing evidence and diff, the owner may explicitly promote it to config.json.

## Derivation rules and insufficient-data behavior
1. dormant_after_days = max(30, ceil(4 × median historical posting gap in days)). With fewer than five dated posts, default 60 remains source=default, confidence=low.
2. min_posts_for_baseline_by_format: examine chronological positive-reach, complete four-metric samples. Seek the earliest N whose medians of sends/reach, saves/reach, likes/reach and follows_gained/reach all move by no more than the configurable relative change after **three further consecutive posts**. Default tolerance 10%, minimum candidate N=6. A one-step flat median, all-zero signals, sparse rows or unstable series keep default=12 and explain why. This is a heuristic stability check, not statistical significance.
3. ghost_self_baseline: requires >=5 earlier active-period positive-reach posts AND historical follower count supplied with --growth. Computes earlier reach/follower median and MAD; with one supplied historic story_views_median and no historical dispersion, a story decline CANNOT be statistically assessed. Without this evidence ghost_risk=unknown.
4. No evidence in the specified CSV can calibrate follower cold-start floors, cold-start post count, has_audience threshold or the baseline window duration. They remain source=default with low confidence. No extrapolation from sparse data.

A derived threshold includes value, source=derived, confidence and evidence (date window, n, method); a default includes source=default and explicit insufficient_data evidence. The proposal is not active until manually reviewed. Older inactive and Trial posts should not be treated as directly comparable to current non-Trial performance.

## Limitations
Median stability is sensitive to chronological order, sample selection, zero denominators, seasonality, campaign objective, reach collection age and even chance. A derived N cannot prove statistical power, causal impact or audience authenticity. There is no universal healthy reach/follower ratio. A declining ratio in a dormant account is confounded: first run a reactivation measurement window. Only a manual follower sample can yield a sample percentage, never a population estimate.

## Owner approval
1. Inspect input provenance and sample size, no synthetic/customer secrets in Git.
2. Inspect each default versus derived threshold and confidence.
3. Inspect the printed diff and ensure every derived rule includes real brand evidence.
4. Rename the reviewed proposal into the private brand config.json manually.
5. Rerun python3 -m scripts.account_state path/to/account.json --config path/to/config.json.
6. Document the review date and reverse or recalibrate when account format, audience or activity pattern materially changes.
