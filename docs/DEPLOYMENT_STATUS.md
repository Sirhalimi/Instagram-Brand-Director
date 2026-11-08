# Development status — 2026-11-09

## Verified in GitHub
- Main SKILL.md, README, all fifteen module definitions and human approval rules.
- Three original offline decision engines: catalog guard, post-Trial review and campaign routing.
- `scripts/creative_quality.py`: locale-aware structural lint, with original English tools and separate Persian checks.
- 41 upstream files copied byte-identically from six repositories, SHA-checked in `docs/UPSTREAM_SOURCE_MANIFEST.json` and with their original MIT/Apache-2.0 licenses.
- 49 Python regression, smoke and provenance tests. The latest GitHub CI status must be checked in Actions; do not assume it remains green after future edits.

## Not yet operational
- Real Instagram OAuth, live Insights synchronization, messaging and API publishing/Trial switching.
- Live ecommerce catalog and supplier stock integrations.
- Generative media tool accounts, paid-ad execution and marketing spend (intentionally optional).
- Complete recursive dependency closure for every vendored instruction file.
- Validated predictions of growth, viral potential or Persian creative performance.
- Completion of mirroring the historical local v0.4 ZIP with 78 files/44 previously reported local tests.

## Important distinction
The 49 GitHub test cases and the older 44 tests reported for the local v0.4 bundle are separate releases. Do not add them together or claim the old bundle has been fully published.

## Data safety
Actual brand profiles, private Insights, inventory, credentials, tokens and customer information must stay outside this public repo. Never execute paid spend, publishing or unsolicited outreach without explicit approval.
