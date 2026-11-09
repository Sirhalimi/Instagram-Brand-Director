# Changelog

## 0.8.0-dev-phase2 — 2026-11-09
- Imported the owner-provided 11,359-byte Instagram rules knowledge file verbatim into repository and installable Skill; recorded SHA-256 and provenance in knowledge/IMPORT_MANIFEST.json. Did not modify third_party/.
- Added stdlib-only scripts/knowledge_age.py to parse Verified headers, dated source-tagged facts, [CONFLICT], [UNVERIFIED], and undated conflict notes with configurable 60-day staleness.
- Added regression fixture and tests plus non-blocking CI knowledge freshness reporting; no live Meta source re-verification claimed.
- Added source hierarchy and evidence-tag honesty to the lean SKILL.md router; documented provisional/offline claims.
- Added direct CLI checks on the Phase-1 synthetic account examples and calibration proposal.
- Kept Phase-3 mandatory account-state preflight and real agent evaluation as not-implemented.

## 0.8.0-dev-phase1 — 2026-11-09
- Added standalone deterministic account-state classification (NO_DATA, COLD_START, DORMANT, ACTIVE_LOW_DATA, ACTIVE_WITH_BASELINE) and per-format median/MAD first-party baselines with n and explicit missingness.
- Added conservative ghost-risk diagnostics that require prior active-period self-baseline; dormant confidence capped at low; manual samples under 30 never imply a percentage.
- Added synthetic account-state and calibration examples; proposed thresholds include default/derived evidence and confidence.
- Added threshold calibration from brand cadence, multiple-step per-format median stability and prior active-period reach/follower history; proposal is never auto-approved or overwritten.
- Shipped both tools at repository scripts/ and inside the installed Skill. Added 29 new regression tests and extended runtime parity checks.
- New module 00 increases file count to 16; old fixed-count tests and Skills CLI smoke test were explicitly updated. Mandatory module-00 router wiring is deferred to Phase 3 and marked not-implemented.
- Kept third_party/ untouched, real brands/ ignored, source data offline, and historical analytics CSV contract unchanged.

## 0.7.0-dev — 2026-11-09
- Added audited baseline builder from validated posts.csv: pooled event/reach rates, comparable observation ages, minimum independent posts/reach, and explicit human comparability review; low samples cannot create strong learnings.
- Tightened posts.csv contract to require source and campaign goal for every record; rates can legitimately exceed 1 due to repeat interactions.
- Added safe real-model evaluation **harness** with offline prepare mode and explicit opt-in Codex CLI execution; no live model evaluation has been run yet.
- Added manual GitHub Actions workflow_dispatch for one synthetic behavior fixture only, requiring a configured key and explicit run; regular CI never invokes paid models.
- Protected new-sales campaigns against unknown unit costs/margins, inconsistent no-camera policies, and invalid boolean flags; added regression tests.
- Added parity test so checked root Python engines and the installed Skill cannot silently diverge.
- Added `agents/openai.yaml` metadata and verified its inclusion during real CLI installation.
- Added five synthetic cross-brand regressions and a Persian human review rubric for the opt-in model evaluation.

## 0.6.0-dev — 2026-11-09
- Refactored to `skills/instagram-brand-director/`: short router + **15 independently loadable modules**. Removed root `SKILL.md` to prevent duplicate discovery.
- Verified **real `npx skills add`** installation in GitHub Actions; installed package excludes `.github/`, test and eval directories from repository root.
- Built bilingual `fa`/`en` localization files and an extensible locale registry. Persian copy is not evaluated using English Hook scores.
- Separated platform facts into dated `knowledge/instagram-rules.md`; references reviewed weekly when current verification is available, stable instructions monthly. Automatic policy monitoring remains not-implemented.
- Introduced offline `brand.md`, `baseline.md`, `posts.csv` templates, JSON schema descriptions and strict validators; missing metrics are not silently zero.
- Replaced low-evidence Trial conclusions with `INSUFFICIENT_DATA`, requiring minimum reach and independent comparable baseline posts; 72h alone is not sufficient.
- Added guarded learning assessment: no single-post generalization and no automatic `learnings.md` writes.
- Added deterministic router/file-budget tests and ten bilingual fixed agent behavior fixtures. **LLM runtime evaluations not run**; do not conflate with unit tests.
- Pinned upstream commit SHA, imported_on and verified_on for 41 identical third-party files; 21 selected licensed source files copied into installable Skill.
- Status of every module and key integration now tracked in `references/implementation-status.json`, including explicit `not-implemented` entries and disabled optional flags.

## 0.5-dev — 2026-11-09
- Imported directly copied sources from six reference repositories; preserved original licenses.
- Added offline campaign, product catalog, Trial and English/Persian creative analysis tools plus tests.

## Historical
- Previous local v0.4 ZIP was not fully reconciled with GitHub. It remains a separate legacy artifact, not a shipped feature set.

