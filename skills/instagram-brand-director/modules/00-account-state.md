# Module 00 — Account-state classification / وضعیت پیج

**Implementation:** deterministic offline scripts/account_state.py and scripts/calibrate_thresholds.py. Classification is implemented; mandatory router integration belongs to Phase 3.

Load when the user provides account analytics or asks for a strategy that depends on whether the page is new, dormant, data-poor or baseline-rich. Do not infer state from follower count alone. All metrics not supplied are **missing**, not zero. Do not use unofficial "healthy engagement" norms.

## Required minimal evidence
- Actual followers (zero is allowed).
- Explicit posts array. An empty array means known zero posts; an omitted array means no history was supplied.
- Every supplied post must have a valid date. A missing or invalid date blocks activity classification.
- Optional today: ISO YYYY-MM-DD; provide it in tests. Current system date is used otherwise.
- Optional approved config.json beside input or via --config. Pending config.proposed.json is NEVER activated automatically.

## Deterministic procedure
1. Run python3 -m scripts.account_state <input.json> [--config <approved-config.json>].
2. Check state, reasons, missing_data, confidence, thresholds_used (each has value and source).
3. NO_DATA → REQUEST_CRITICAL_DATA only; explicitly list missing followers/posts/posts[].date.
4. COLD_START → original, practical discovery experiments, not Trial eligibility claims.
5. DORMANT → reactivation measurement window, baseline=null, ghost_risk confidence capped to low.
6. ACTIVE_LOW_DATA → collect positive-reach same-format samples and nonmissing metrics; do not invent rates.
7. ACTIVE_WITH_BASELINE → compare per-format medians and median absolute deviations (MAD), each with n. Avoid follower-normalized likes or mean-of-ratios shortcuts.
8. Ghost risk is always unknown without an earlier active-period self-baseline; no percentage estimate from raw reach/followers. A manual sample smaller than 30 cannot be generalized.
9. Trial eligibility: 0–199 followers → no (conservative provisional threshold); 200–999 → unknown unless native toggle observed; >=1000 → unknown unless native toggle observed. Account Status explicitly ineligible → no. Phase 2 supplies dated conflicting claims; never present these cutoffs as confirmed official rules.

## Config / source of thresholds
Defaults are UNCALIBRATED, editorial-only heuristics: cold_start_max_followers=50, cold_start_max_posts=5, dormant_after_days=60, min_posts_for_baseline=12, baseline_window_days=90. has_audience_min_followers=200 is also a UI strategy heuristic. Each result includes source=default or source=derived. Derive from brand-specific history only with scripts/calibrate_thresholds.py. Review and approve config.proposed.json before renaming to config.json.

## Safety
Originality risk is UNKNOWN without actual rights/origin evidence; Account Status recommendation eligibility only controls restricted, not fake follower classification. Never automatically remove followers, spend, publish, authenticate or write learnings.md. These scripts have no network calls and require no credentials.
