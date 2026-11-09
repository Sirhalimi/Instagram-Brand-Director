# Development status — 2026-11-09 (0.8.0-dev-phase5)

## Phase 5 of 5 — behavior fixtures ready, real model evaluation NOT executed
- Six synthetic standalone tests/behavior/*.json fixtures include input prompts and separate decision/state expectations, forbidden outcomes and human reviewer requirements.
- Offline Python tests now exercise existing route, account-state, campaign, post-intake and review gates against the six scenarios. This is deterministic contract testing and **not an LLM-generated-answer test**.
- The optional Codex eval harness accepts an explicitly supplied fixture directory; prepare creates isolated Skill workspaces and stores per-case rubric.json outside the agent workspace. Expected answers are not put in the prompt.
- A phase-5 response's lexical grade is NOT_GRADED and requires human review rather than a misleading PASS. Live responses/trace have not been collected in this environment.
- Existing root ten-fixture suite remains available; live trial/publishing/ads/DM execution is not implemented.
- No real brand data, secrets or client context have been included in public fixtures. New scripts use standard library and no background network calls.

## Phase 4 of 5 — implemented offline, live integrations not implemented
- Per-source media rights gate distinguishes actual publishable assets from third-party references used ONLY for research, with explicit watermark/permission fields and rejection of subtitles-only reposts. Rights assertions are self-reported and require human documentation.
- Availability adapters for physical_stock (legacy unchanged), digital_product, cohort_seats and consult_slots are used by campaign_decision and catalog_guard. Zero seats/slots, unavailable digital fulfillment/licenses, stale data and unknown cost/margin stop new-sales promotion.
- Original physical-stock tests are unchanged and must continue passing; no new external Python dependencies or network access.
- Live license checks, Meta content rights verification, actual supplier/calendar/slot lookups, posting and transactions remain not-implemented.
- Successful fixture tests or `PROMOTE` never means a public asset was legally cleared or a real item has been reserved.

## Phase 3 of 5 — deterministic implementation, not live LLM validation
- Module 00 is now required by the Skill router *before brand-specific strategy and format decisions*. Missing account evidence triggers REQUEST_CRITICAL_DATA. Fixed-format caption drafts and immediate product safety refusals remain unblocked.
- All 16 modules carry a concrete scope/status in the primary SKILL.md and implementation-status.json: implemented (offline scope only), spec-only, or not-implemented. Installed adapters for Meta publishing, real Insights and paid advertising remain not-implemented.
- Private brand profiles may contain reviewed post_defaults for camera presenter, exact target audience, excluded audience, post goal and production capacity. scripts/post_intake.py is read-only by default; explicit --save and durable_keys are required for persistence.
- General strategic reviews use an approved-config-derived sample threshold or uncalibrated N=12 default via scripts/review_gate.py, never infer a pattern from 1–2 posts. The existing one-off Trial gate retains its independent six-post/reach operational prerequisites. No automatic learnings.md write occurs.
- Human Persian copy review checklist includes half-spaces/ZWNJ, tone, RTL text, hashtags and subtitles. English-only hook scoring remains unsupported in Persian.
- Phase 3 tests verify deterministic routing/data handling but do NOT constitute actual agent-generated-response evaluation. No external connectors were enabled.

## Phase 2 of 5 — implemented and tested
- User-provided Instagram knowledge file has been imported byte-identically to root and installed Skill; see knowledge/IMPORT_MANIFEST.json. Existing generic placeholder was replaced, not merged.
- Offline knowledge_age CLI audits the file-level Verified date, dated claim entries, source conflicts and unverified/undated notes; it does **not** verify factual accuracy online.
- Stale dates fail the CLI with exit code 1, but the GitHub Actions advisory step has continue-on-error=true so unrelated tests still pass.
- Source hierarchy and tag restrictions are included in the primary Skill router. A claim tagged OFFICIAL in the owner-provided registry is not independently verified by this import.
- Current supplied file is marked REVIEW_REQUIRED because unresolved conflicts and unverified entries remain; these are not silently promoted to platform facts.
- Live policy refresh remains not-implemented. Mandatory account-state routing was implemented as a procedural/deterministic gate in Phase 3, without live agent evaluation.

## Phase 1 of 5 — implemented and tested
- Offline account-state classifier distinguishes NO_DATA, COLD_START, DORMANT, ACTIVE_LOW_DATA and ACTIVE_WITH_BASELINE. Positive-reach per-format rates use median and MAD; all report n.
- Conservative provisional Trial eligibility bands; official source conflicts (200 vs 1,000) must be reconciled with the owner's exact Phase-2 knowledge file before they are treated as dated facts.
- Proposed threshold calibration from observed cadence, per-format multi-step median stability and available historical self-baselines; no approved config is overwritten.
- All Phase-1 fixtures are synthetic. No network or credentials. Default threshold values remain labeled uncalibrated assumptions.
- Module 00 was added in Phase 1 and made a mandatory pre-strategy gate in Phase 3; live LLM behavior has not been independently evaluated. Existing 15-module count assertions were intentionally revised to 16.
- The calibration posts.csv schema has columns date/format/topic/hook/... and is not identical to the pre-existing validation export schema with post_id/published_at/goal/source; no implicit format conversion exists.

## Verified
- Evidence-based baseline builder is executable and tested; posts.csv requires goal/source and baseline comparability is withheld unless explicitly reviewed and sampled adequately.
- Optional Codex CLI eval harness has offline preparation and tests; a manual one-case GitHub workflow is installed. **No real model-run evaluation results have been produced**; agent runtime eval remains not-implemented until a controlled run succeeds and is reviewed.
- Commercial promotion fails closed when cost or margin cannot be established; camera-policy conflicts cannot pass silently.
- **One installable Skill:** `skills/instagram-brand-director/SKILL.md` plus 16 on-demand modules.
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

