# Instagram Brand Director

**Version: `0.8.0-dev-phase3` · 2026-11-09**

A bilingual (فارسی / English), modular, evidence-aware **Instagram Social Media & Marketing Director** Agent Skill. It gives one accountable next action for strategy, but responds directly with usable copy for lightweight requests. Third-party tools are reused where they are demonstrably useful; inventory/Trial safeguards are original and conservative.

## Install / نصب

The actual Vercel Skills CLI installation has been tested on GitHub Actions with Codex. The CLI installs only the selected nested Skill directory, **not the entire repository**.

```bash
npx skills add Sirhalimi/Instagram-Brand-Director --skill instagram-brand-director -a codex -y
```

Installed directory: `.agents/skills/instagram-brand-director/` (the agent may symlink to it). A nested `SKILL.md` is the only entrypoint. Root `SKILL.md` was removed to prevent duplicate discovery.

## Architecture / معماری

```text
skills/instagram-brand-director/
├── SKILL.md                         # short selective router
├── modules/                         # 16 independent on-demand files (modules 00–15)
├── knowledge/instagram-rules.md      # dated, weekly-reviewed facts
├── knowledge/learnings-governance.md
├── locales/{fa,en,registry.json}    # two supported languages, extensible
├── schemas/                         # brand / baseline / posts contracts
├── templates/                       # synthetic private brand templates
├── scripts/                         # offline routing, checks and analysis
├── references/implementation-status.json
├── references/source-attribution.json
└── third_party/                     # selected licensed upstream tools
```

**File-loading budget:** ordinary caption/Reel/audit request = router + one primary module (**2 files**). Mixed commercial creative can require one extra module (**3 files**). Platform-specific rules may require knowledge (**up to 4 files**). These budgets are tested by `router_probe.py`; actual model file reads still require separate agent-run evaluation.

## Two response modes

- **Production / تولیدی:** give the finished caption, Reel script, carousel plan or Story first, without a five-section strategy memo. If camera availability is unknown, ask once *before the first Reel production brief*, not before a caption.
- **Strategy / تصمیم مدیریتی:** one choice + evidence + rejected alternative + execution + predeclared review trigger. Do not flatter unsupported ideas, fabricate metrics or guarantee reach.

## Trial noise and learnings

Conservative default decision gates (not Instagram rules): **Trial reach ≥300; ≥6 comparable historical posts; ≥1800 pooled historical reach; comparable first-party data; review age ≥24h**. Below the gates, the decision is `INSUFFICIENT_DATA`, including after 72h. A single promising Reel never proves a recurring pattern. `learning_gate.py` only produces a human-review candidate after repeated independent evidence; it never writes `learnings.md`.

## Private data validation / اعتبارسنجی داده

Copy `templates/brand.md`, `templates/baseline.md`, and `templates/posts.csv` to a **private brand workspace**. Fill in real data, then:

```bash
python3 skills/instagram-brand-director/scripts/validate_data.py brand /private/brand.md
python3 skills/instagram-brand-director/scripts/validate_data.py baseline /private/baseline.md
python3 skills/instagram-brand-director/scripts/validate_data.py posts /private/posts.csv
```

`brand.md` and `baseline.md` contain one fenced JSON object; the CSV uses explicit column types and timezone-aware timestamps. Validation means format integrity, **not** that metrics are sufficient for inference. Missing fields must not be silently treated as zero.

Run the installed engines from the skill directory:

```bash
cd skills/instagram-brand-director
python3 -m scripts.router_probe 'برای برندم کپشن بنویس'
python3 -m scripts.creative_quality hook --text '۳ اشتباه رایج در خرید لباس'
python3 -m scripts.trial_review ../../examples/trial-review.sample.json
```

## Status, evidence and licenses

- Full specification: **16 modules (00–15)**, with core decision workflows operating offline and external integrations explicitly tracked as partial or `not-implemented`.
- Language: **fa / en supported**; other languages require a locale file, registry change, and regression tests. English-only upstream Hook scores are **not validated for Persian**.
- Source provenance: **41 byte-identical files from six GitHub repositories** in the development repo; **21 selected source files** ship inside the installed Skill. Original MIT/Apache-2.0 licenses are retained. `docs/UPSTREAM_SOURCE_MANIFEST.json` and the installed `references/source-attribution.json` record source commit SHA and import date.
- Live Instagram OAuth/Insights, store API sync, real publishing and paid-ad execution remain **not-implemented**. Media-generation and paid-ad integrations are **optional and disabled** until explicitly authorized.
- CI: Python/unit/contract tests **and a real Skills CLI installation smoke test**. Fixed bilingual agent behavior fixtures are in `evals/`; actual LLM-generated response evaluation is **not executed** in this environment and must not be confused with code tests.

See [the Persian agent eval runbook](docs/AGENT_EVAL_RUNBOOK_FA.md), [implementation status](skills/instagram-brand-director/references/implementation-status.json), [change log](CHANGELOG.md), [agent eval fixtures](evals/agent-scenarios.json) and [release checklist](docs/RELEASE_CHECKLIST_FA.md).


## Evidence-first baselines and real-agent evaluation (v0.7-dev)

A new offline `scripts/baseline_builder.py` derives **pooled reach-normalized rates** from posts.csv rather than trusting a manually typed average. CSV now requires each post's `goal` and `source`; `metrics_age_hours` can establish comparable observation horizons. The generated baseline stays `INSUFFICIENT_DATA` until the sampling floors, time windows and explicit human comparability review pass. Data-source labels are user-supplied and do not prove API provenance.

```bash
cd skills/instagram-brand-director
python3 -m scripts.baseline_builder --brand /private/brand.md --posts /private/posts.csv --start 2026-10-01 --as-of 2026-11-09 --goal discovery --format reel --output /private/baseline.md
```

An optional real-model eval runner is available, **but no live Codex model evaluations have been executed in this release**. Offline mode is safe and cost-free:

```bash
python3 tools/run_agent_eval.py --mode prepare --output /tmp/igbd-eval-prep
```

To deliberately run one synthetic case on an already authenticated Codex CLI (may consume model usage), invoke:

```bash
python3 tools/run_agent_eval.py --mode run --case fa_sold_out --allow-model-usage --output /tmp/igbd-eval-live
```

The [opt-in GitHub workflow](.github/workflows/agent-eval.yml) provides a one-case manual alternative after configuring a repository `OPENAI_API_KEY` secret. It does **not run on push or PR**. Model response logs, weak mechanical checks and raw trace are always for **human evaluation**, not a pass certificate. The public CI continues using deterministic fixtures and a real Skills CLI installation smoke test.

## Phase 1 of 5 — account-state classification and proposed calibration

**Status:** Account classification and per-brand calibration CLIs are implemented and covered by synthetic tests. Mandatory routing through module 00 is **not implemented until Phase 3**; the main router is intentionally unchanged in this phase.

```bash
python3 -m scripts.account_state examples/account-state.zero-follower-editorial.sample.json
python3 -m scripts.account_state examples/account-state.dormant-digital-store.sample.json
python3 -m scripts.account_state examples/account-state.established-wholesale.sample.json
python3 -m scripts.calibrate_thresholds examples/calibration.wholesale.posts.sample.csv --growth examples/calibration.wholesale.growth.sample.json --today 2026-11-09 --output /tmp/config.proposed.json
```

The classification covers NO_DATA, COLD_START, DORMANT, ACTIVE_LOW_DATA, and ACTIVE_WITH_BASELINE; current-format baselines report per-reach medians, median absolute deviations and sample sizes. Missing observations remain missing. Ghost/fake-follower risk remains **unknown** without earlier first-party self-history. No automated mass removal, publication, or account modifications.

Calibrated thresholds are submitted as config.proposed.json only. The owner must review their provenance and explicitly promote the file to the private brands/<slug>/config.json. Default thresholds remain labeled uncalibrated editorial assumptions, NOT Meta rules. The new calibration CSV schema is distinct from the earlier analytics posts.csv schema and is not silently converted.

Read [Strategy by State](docs/STRATEGY_BY_STATE.md) and [Calibration/approval](docs/CALIBRATION.md). All committed examples are synthetic; brands/ remains Git-ignored.

## Phase 2 of 5 — source-tagged, dated Instagram knowledge

The original, user-provided `instagram-rules.md` (11,359 UTF-8 bytes) is preserved **unchanged** at both `knowledge/instagram-rules.md` and the installable Skill's `skills/instagram-brand-director/knowledge/instagram-rules.md`. The SHA-256 and import provenance are in `knowledge/IMPORT_MANIFEST.json`. The previous generic knowledge placeholder was replaced rather than merged, to avoid changing the supplied content.

```bash
python3 -m scripts.knowledge_age knowledge/instagram-rules.md --as-of 2026-11-09 --max-age-days 60
python3 -m scripts.knowledge_age knowledge/instagram-rules.md --as-of 2027-02-01 --max-age-days 60
```

Output includes the file-level Verified age, each dated entry older than the limit, and unresolved `[CONFLICT]`/`[UNVERIFIED]` entries (including an undated prefix-tagged conflict). Exit codes: 0 = no stale dates (review flags may still exist); 1 = stale file header or entry; 2 = malformed dates or inputs. The CI knowledge check uses `continue-on-error: true` so staleness is visible but does **not** block unrelated development.

**Source priority:** first-party account data for brand performance; official Meta/Instagram for platform policy; reported secondary sources; community-skill assumptions. Preserve labels `OFFICIAL`, `REPORTED`, `SINGLE-SOURCE`, `CONFLICT`, `HYPOTHESIS`, and `UNVERIFIED`. Dated facts can be consulted with qualification; marketing formulas and posting-frequency promises are hypotheses. An older-than-60-day entry needs current verification if online, or a provisional/stale label offline. The user-supplied claim tags have **not** been individually re-verified in this phase.

**Not yet implemented:** automated weekly Meta refresh, resolution of conflicting eligibility claims, and the mandatory account-state routing change planned for Phase 3.

## Phase 3 of 5 — mandatory account-state routing, honest module status, and private post intake

For a real brand's strategy or **format/distribution selection**, the Skill now requires module `00-account-state.md` *before* a plan. If first-party follower count or dated post history is missing, the correct response is `REQUEST_CRITICAL_DATA`, not generic advice. Already-chosen simple copy, translation and immediate `DO_NOT_PROMOTE` safety refusals are exceptions. This is an **instruction-level** gate plus a deterministic router probe: an actual model-output behavioral eval has **not yet been executed**.

```bash
# Lightweight route budget and decision-gate prediction
python3 skills/instagram-brand-director/scripts/router_probe.py "Create a monthly content calendar"
# Read-only post intake: synthetic example, no real-brand data
python3 skills/instagram-brand-director/scripts/post_intake.py --brand skills/instagram-brand-director/templates/brand.md --post examples/post-intake.sample.json
# General account learning/review gate: default N=12 unless approved derived config overrides
python3 -m scripts.review_gate examples/review-gate.sample.json
```

The **16-module status table** in the installed `SKILL.md` and `references/implementation-status.json` now uses `implemented`, `spec-only`, and `not-implemented`. Executable modules are explicitly **offline**, without Instagram publishing/Insights access. A spec-only module is guidance or a draft, not a completed integration.

`post_intake.py` asks only unknown **on-camera person (video only), exact audience, excluded audience, post goal (trust/saves/sends/leads/sales), and production capacity**. It reads supplied private `brand.md` and post JSON only; `--save` plus an explicit answers JSON and `durable_keys` is required to atomically persist stable defaults in that provided brand file. A single-shoot answer is not silently turned into a durable preference.

For **generalized strategy/review conclusions**, `review_gate.py` uses the account's approved config's derived per-format minimum N where present, otherwise the uncalibrated default **N=12**; too little or unverified data means `INSUFFICIENT_DATA`. The existing separate **Trial one-post operational gate** retains its previous minimum (6 comparable historical posts plus reach floors); passing a Trial gate does **not** establish a repeatable account pattern.

Persian output now has [a human review checklist](docs/PERSIAN_REVIEW_CHECKLIST.md) covering ZWNJ, formal/colloquial consistency, RTL overlays, hashtags, subtitles and evidence. English-only `hookscore.py` remains **unsupported for Persian**. No real brand data belongs in Git.

**Phase 4 remains not-implemented:** third-party production-rights policy and generalized digital/service availability adapters have not been started in this phase.

## Reference projects

[social-media-skills](https://github.com/social-media-skills/skills) · [Jake Instagram Agent Skill](https://github.com/Jakeschincariol/instagram-agent-skill) · [Instagram Skills](https://github.com/sergebulaev/instagram-skills) · [Marketing Skills](https://github.com/coreyhaines31/marketingskills) · [Digital Marketing Skills](https://github.com/vidual-labs/digital-marketing-skills) · [Apify Awesome Skills](https://github.com/apify/awesome-skills).

