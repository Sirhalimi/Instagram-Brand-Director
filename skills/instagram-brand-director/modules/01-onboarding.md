# Brand onboarding and capability diagnosis

**Scope:** Instagram Brand Director module 01

**Reference implementations:** S: brand-profile; M: customer-research/product-marketing. Source materials are preserved under repository `third_party/` or referenced in `references/source-attribution.md`; only selected vetted tools ship with the installed Skill.

## Load this module when
Requests concern brand onboarding and capability diagnosis; do not load other modules unless the task requires their data or permissions.

## Procedure
1. Ask for a concise business description, desired result, current pain, products/offers and existing channels; read provided website/previous records before asking. Avoid re-interviewing if a current brand profile exists.
2. Identify buyer vs follower, value proposition, competitors, brand voice, proof, preferred and forbidden claims; document the actual problem before content ideas.
3. Inventory production constraints: camera access, on-camera willingness, voiceover, equipment, time/week, editing/design capabilities, team/budget and media rights.
4. Collect commercial dependencies: catalog URL/export, variants, currency, prices, COGS, stock policy, stock timestamp, supplier reliability, margin, fulfillment, return rules. Missing or stale facts remain unknown.
5. Save brand.md using templates/brand.md and run `python3 -m scripts.validate_data brand brand.md`. Save private brand data outside this public repository.

## Output
Validated brand.md, one-sentence diagnosis, ranked constraints, first decision and missing-data list.

## Guardrails and implementation gaps
No invented personas, prices, views or stock. For new brand ask one short question at a time. Never require camera-facing content.

## Language and evidence
Write in the brand's preferred locale (currently `fa` or `en`); preserve exact product names and numeric data. All public Meta claims must be checked against `../knowledge/instagram-rules.md` and dated sources. Missing metrics are unknown, never invented. Use `../references/response-contracts.md` for the response appropriate to the request.
