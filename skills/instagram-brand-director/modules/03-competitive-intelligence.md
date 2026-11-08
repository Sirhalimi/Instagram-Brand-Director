# Competitors and trend research

**Scope:** Instagram Brand Director module 03

**Reference implementations:** J: ig-viral/swipe.py; S: competitor-analysis, trend-jacking; A: apify-ads-intelligence. Source materials are preserved under repository `third_party/` or referenced in `references/source-attribution.md`; only selected vetted tools ship with the installed Skill.

## Load this module when
Requests concern competitors and trend research; do not load other modules unless the task requires their data or permissions.

## Procedure
1. Define direct, indirect and category-adjacent competitors; verify public handles before comparing.
2. Collect public Reel samples with date, views, account median where available, format, hooks, audio context, caption, content purpose. Use vendored swipe.py on user-collected TSV, not unauthorized scraping.
3. Compare each competitor with its own baseline where known; flag cross-account reach/follower comparisons as weak proxies.
4. Evaluate trends by brand fit, novelty, time sensitivity, rights, production feasibility, stock and business objective.
5. If Apify is explicitly connected, use permitted access with costs and limitation disclosed; otherwise cite the public Meta Ad Library or request exports.

## Output
Evidence table, three defensible opportunities, one selected experiment.

## Guardrails and implementation gaps
Do not infer competitor sales, conversion rate or profitability from public view counts.

## Language and evidence
Write in the brand's preferred locale (currently `fa` or `en`); preserve exact product names and numeric data. All public Meta claims must be checked against `../knowledge/instagram-rules.md` and dated sources. Missing metrics are unknown, never invented. Use `../references/response-contracts.md` for the response appropriate to the request.
