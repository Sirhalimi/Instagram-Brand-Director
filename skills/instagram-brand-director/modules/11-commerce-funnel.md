# Catalog, inventory, offers, pricing, conversion

**Scope:** Instagram Brand Director module 11

**Reference implementations:** Original catalog_guard.py; M: product-marketing, offers, attribution, conversion-tracking. Source materials are preserved under repository `third_party/` or referenced in `references/source-attribution.md`; only selected vetted tools ship with the installed Skill.

## Load this module when
Requests concern catalog, inventory, offers, pricing, conversion; do not load other modules unless the task requires their data or permissions.

## Procedure
1. Select the explicit availability model from the private offer record: `physical_stock` (stock/supplier), `digital_product` (license validity, verified automatic/manual/supplier delivery and regional restrictions when relevant), `cohort_seats` (seats, start and enrollment status), or `consult_slots` (open slots, verified response time and service capacity). Missing type preserves the old physical flow; unknown type blocks. If product is obviously unavailable, immediately reject new-sale promotion with DO_NOT_PROMOTE; do not delay safety refusal for account metrics. Before other brand campaign/format choices run module 00. Read full product and offer catalog with SKU, options, in-stock/supplier checks, local currency, last-verified price, cost, gross margin, target, lead time, restrictions, returns and checkout link.
2. Before selecting an offer for promotion, execute catalog_guard.py for its availability type. Zero stock, invalid digital license, broken delivery automation, full cohort, zero consultation slots, stale quote or unverified fulfillment → DO_NOT_PROMOTE for **new sales**. A valid offline assertion does not establish live supplier/calendar availability.
3. Distinguish marketing awareness from direct checkout promises. Paid ads require current unit economics; do not authorize below-margin budget from guesswork.
4. Audit Instagram → bio/link/DM → product page → checkout → delivery → retention path. Trace UTM and conversions without claiming causal attribution unsupported by data.
5. Suggest one eligible product or remedial conversion fix. Preserve accepted customer obligations even when newer stock has changed.

## Output
Verified campaign offer, product eligibility report and next sales-funnel action.

## Guardrails and implementation gaps
Do not cancel/refuse already-accepted paid obligations because a later marketing eligibility check failed; those must be fulfilled or resolved under separate owner-approved operations. Configurable response SLAs and campaign margin floors are business policies, not Instagram facts. All nonphysical adapters are offline-only. Live store API and inventory sync: not-implemented; use fresh owner exports until integrated.

## Language and evidence
Write in the brand's preferred locale (currently `fa` or `en`); preserve exact product names and numeric data. All public Meta claims must be checked against `../knowledge/instagram-rules.md` and dated sources. Missing metrics are unknown, never invented. Use `../references/response-contracts.md` for the response appropriate to the request.
