# Performance analysis, A/B tests and learning

**Scope:** Instagram Brand Director module 14

**Reference implementations:** J: ig-audit; S: analytics-and-reporting; M: analytics, conversion-tracking. Source materials are preserved under repository `third_party/` or referenced in `references/source-attribution.md`; only selected vetted tools ship with the installed Skill.

## Load this module when
Requests concern performance analysis, a/b tests and learning; do not load other modules unless the task requires their data or permissions.

## Procedure
1. Load only validated brand.md/posts.csv or permitted first-party API results. Build a pooled first-party baseline via `scripts/baseline_builder.py`; retain `comparable=false` and `INSUFFICIENT_DATA` if observation ages, sample floors or manual representativeness review are absent. Verify metric definitions, dates and provenance.
2. Compare like-for-like formats and campaign objectives using weighted reach-normalized rates; watch time must have duration context; avoid cross-account causal claims.
3. Design a clear A/B hypothesis with a primary metric, minimum sample, comparison group and predeclared evaluation time. Do not silently redefine success after results.
4. Report what improved, what remains uncertain, and one next action with follow-up review date.
5. Store private observations per brand. **Do not append any asserted pattern to `learnings.md` based on 1–2 posts or low reach.** Use `scripts/learning_gate.py` for at least 4 independent comparable posts, >=300 reach each and >=3000 pooled reach (brand-configured defaults); even passing gate creates only a human-review candidate, never an automatic memory write.

## Output
Decision report with evidence and uncertainty classification.

## Guardrails and implementation gaps
Live scheduled Insights sync and analytics dashboard: not-implemented; offline validated analysis can still run.

## Language and evidence
Write in the brand's preferred locale (currently `fa` or `en`); preserve exact product names and numeric data. All public Meta claims must be checked against `../knowledge/instagram-rules.md` and dated sources. Missing metrics are unknown, never invented. Use `../references/response-contracts.md` for the response appropriate to the request.
