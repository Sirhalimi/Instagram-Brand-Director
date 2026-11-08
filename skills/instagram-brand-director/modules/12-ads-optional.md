# Influencer strategy and optional paid-ad execution

**Scope:** Instagram Brand Director module 12

**Reference implementations:** M: influencer-marketing/ads; A: apify-ads-intelligence; S: UGC. Source materials are preserved under repository `third_party/` or referenced in `references/source-attribution.md`; only selected vetted tools ship with the installed Skill.

## Load this module when
Requests concern influencer strategy and optional paid-ad execution; do not load other modules unless the task requires their data or permissions.

## Procedure
1. Advertising strategy and partner vetting are core advice regardless of integration state.
2. Evaluate partners by audience fit, geographic relevance, authenticity, rights, compensation, clear disclosure, ROI measurement and commercial readiness.
3. For paid campaigns set goal, target, authorized budget, creative, landing path and campaign review; do not use guessed reach/CPM as guarantees.
4. Third-party Apify research remains optional, costed and permissioned. Actual Ads Manager execution is disabled until separately activated, authorized and tested.
5. Require explicit approval for any spend, published creative, outreach, attribution settings or account changes.

## Output
Partner/ads strategy with accountable budget conditions; execution only if optional adapter enabled.

## Guardrails and implementation gaps
Actual ad creation, buying and budget adjustment: not-implemented by default. No covert advertising.

## Language and evidence
Write in the brand's preferred locale (currently `fa` or `en`); preserve exact product names and numeric data. All public Meta claims must be checked against `../knowledge/instagram-rules.md` and dated sources. Missing metrics are unknown, never invented. Use `../references/response-contracts.md` for the response appropriate to the request.
