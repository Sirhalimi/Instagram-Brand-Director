# Catalog, inventory, offers, pricing, conversion

**Scope:** Instagram Brand Director module 11

**Reference implementations:** Original catalog_guard.py; M: product-marketing, offers, attribution, conversion-tracking. Source materials are preserved under repository `third_party/` or referenced in `references/source-attribution.md`; only selected vetted tools ship with the installed Skill.

## Load this module when
Requests concern catalog, inventory, offers, pricing, conversion; do not load other modules unless the task requires their data or permissions.

## Procedure
1. Read full product and offer catalog with SKU, options, in-stock/supplier checks, local currency, last-verified price, cost, gross margin, target, lead time, restrictions, returns and checkout link.
2. Before selecting a product for promotion, execute catalog_guard.py. Out-of-stock, stale pricing or unverified fulfillment means DO_NOT_PROMOTE for new sales.
3. Distinguish marketing awareness from direct checkout promises. Paid ads require current unit economics; do not authorize below-margin budget from guesswork.
4. Audit Instagram → bio/link/DM → product page → checkout → delivery → retention path. Trace UTM and conversions without claiming causal attribution unsupported by data.
5. Suggest one eligible product or remedial conversion fix. Preserve accepted customer obligations even when newer stock has changed.

## Output
Verified campaign offer, product eligibility report and next sales-funnel action.

## Guardrails and implementation gaps
Live store API and inventory sync: not-implemented; use fresh owner exports until integrated.

## Language and evidence
Write in the brand's preferred locale (currently `fa` or `en`); preserve exact product names and numeric data. All public Meta claims must be checked against `../knowledge/instagram-rules.md` and dated sources. Missing metrics are unknown, never invented. Use `../references/response-contracts.md` for the response appropriate to the request.
