# Performance analysis, A/B tests and learning

**Scope:** Instagram Brand Director module 14

**Reference implementations:** J: ig-audit; S: analytics-and-reporting; M: analytics, conversion-tracking. Source materials are preserved under repository `third_party/` or referenced in `references/source-attribution.md`; only selected vetted tools ship with the installed Skill.

## Load this module when
Requests concern performance analysis, a/b tests and learning; do not load other modules unless the task requires their data or permissions.

## Procedure
1. Load only validated baseline.md and posts.csv or permitted first-party API results. Verify metric definitions, sample windows and completeness.
2. Compare like-for-like formats and campaign objectives using weighted reach-normalized rates; watch time must have duration context; avoid cross-account causal claims.
3. Design a clear A/B hypothesis with a primary metric, minimum sample, comparison group and predeclared evaluation time. Do not silently redefine success after results.
4. Report what improved, what remains uncertain, and one next action with follow-up review date.
5. Archive a private experiment log per brand; avoid leaking brand-specific operational data into public Skill source.

## Output
Decision report with evidence and uncertainty classification.

## Guardrails and implementation gaps
Live scheduled Insights sync and analytics dashboard: not-implemented; offline validated analysis can still run.

## Language and evidence
Write in the brand's preferred locale (currently `fa` or `en`); preserve exact product names and numeric data. All public Meta claims must be checked against `../knowledge/instagram-rules.md` and dated sources. Missing metrics are unknown, never invented. Use `../references/response-contracts.md` for the response appropriate to the request.
