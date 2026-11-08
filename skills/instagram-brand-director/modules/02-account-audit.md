# Instagram profile and Insights audit

**Scope:** Instagram Brand Director module 02

**Reference implementations:** J: ig-audit; D: instagram-organic; S: analytics-and-reporting. Source materials are preserved under repository `third_party/` or referenced in `references/source-attribution.md`; only selected vetted tools ship with the installed Skill.

## Load this module when
Requests concern instagram profile and insights audit; do not load other modules unless the task requires their data or permissions.

## Procedure
1. Request authorized Instagram Professional insights or a user-supplied export; never request passwords or session cookies.
2. Validate brand.md and posts.csv before using any metric; missing is not zero. Use `scripts/baseline_builder.py` to derive pooled rates rather than averaging per-post rates, and keep `comparable=false` without explicit review of format, goal, observation horizon, representativeness and source.
3. Audit username, biography, category, profile image, pinned posts, highlights, link destination, content library, account-status recommendation eligibility.
4. Compare like-for-like post formats over declared time windows and sample sizes; use reach-normalized shares, saves, follows, business conversions; interpret watch time relative to Reel length.
5. Identify the top one or two root problems, explicitly separate hypothesis vs observation; produce action with measurable check-in.

## Output
Diagnostic summary, clean data inventory, baseline and prioritized action.

## Guardrails and implementation gaps
No claimed live connection until authorized OAuth and end-to-end fetch verified. Captions/insights may be incomplete by API/account type.

## Language and evidence
Write in the brand's preferred locale (currently `fa` or `en`); preserve exact product names and numeric data. All public Meta claims must be checked against `../knowledge/instagram-rules.md` and dated sources. Missing metrics are unknown, never invented. Use `../references/response-contracts.md` for the response appropriate to the request.
