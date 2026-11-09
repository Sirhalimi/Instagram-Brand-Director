# Development status — 2026-11-09 (0.8.0-dev-phase1)

## Phase 1 of 5 — implemented and tested
- Offline account-state classifier distinguishes NO_DATA, COLD_START, DORMANT, ACTIVE_LOW_DATA and ACTIVE_WITH_BASELINE. Positive-reach per-format rates use median and MAD; all report n.
- Conservative provisional Trial eligibility bands; official source conflicts (200 vs 1,000) must be reconciled with the owner's exact Phase-2 knowledge file before they are treated as dated facts.
- Proposed threshold calibration from observed cadence, per-format multi-step median stability and available historical self-baselines; no approved config is overwritten.
- All Phase-1 fixtures are synthetic. No network or credentials. Default threshold values remain labeled uncalibrated assumptions.
- New module 00 is present but mandatory routing is **not-implemented until Phase 3**. Existing 15-module count assertions were intentionally revised to 16.
- The calibration posts.csv schema has columns date/format/topic/hook/... and is not identical to the pre-existing validation export schema with post_id/published_at/goal/source; no implicit format conversion exists.

## Verified
- Evidence-based baseline builder is executable and tested; posts.csv requires goal/source and baseline comparability is withheld unless explicitly reviewed and sampled adequately.
- Optional Codex CLI eval harness has offline preparation and tests; a manual one-case GitHub workflow is installed. **No real model-run evaluation results have been produced**; agent runtime eval remains not-implemented until a controlled run succeeds and is reviewed.
- Commercial promotion fails closed when cost or margin cannot be established; camera-policy conflicts cannot pass silently.
- **One installable Skill:** `skills/instagram-brand-director/SKILL.md` plus 15 on-demand modules.
- **Real Vercel Skills CLI smoke test succeeded** via GitHub Actions for Codex and verified exclusion of root test/CI/fixture files.
- **Bilingual routing and copy checks** for Persian and English, with conservative no-English-scoring rule for Persian.
- **Private brand data contracts** (`brand.md`, `baseline.md`, `posts.csv`) and offline validator.
- **Conservative Trial evaluation** with explicit reach, comparable sample and pooled baseline gates; evidence insufficient after 72h remains inconclusive.
- **Learning gate** never auto-writes to `learnings.md`.
- **Provenance:** 41 unchanged files from six upstream repositories, origin commit SHA/date recorded; 21 selected copies bundled with Skill, with licenses.
- **CI** runs unit, routing, provenance, behavior-contract, and real installation checks.

## Explicit not-implemented
- Live Instagram OAuth and account binding, ongoing Insights ingestion, automatic Trial or post publishing, outgoing DMs, customer support execution.
- Live store inventory/price/cost/supplier sync, complete marketing attribution, paid-ad execution or media generation integrations.
- Actual LLM agent transcript evaluation (ten deterministic fixtures exist; no model-run pass claimed).
- Statistical validation that Persian caption/Hook heuristics predict performance, additional language packs.
- Automatic weekly monitoring of official Meta policy updates; knowledge must be manually refreshed and cited.
- Full legacy v0.4 ZIP reconciliation and complete transitive dependencies of all third-party SKILL documents.

## Important distinctions
Machine-readable status is `skills/instagram-brand-director/references/implementation-status.json` and must be updated for **every release**. `not-implemented` is a real state, not 'coming soon' completion. The old local v0.4 test count must not be added to current GitHub tests. Passing a deterministic output fixture does not mean an LLM followed the prompt in production.

## Secrets/privacy
Keep all actual brand profiles, source Insights, invoices, stock and customers outside this public repository. No tokens, session cookies, Instagram passwords, ad spend, publishing or external messages without an authorized connector and explicit owner approval.

