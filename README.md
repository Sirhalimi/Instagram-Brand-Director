# Instagram Brand Director

**Version: `0.6.0-dev` · 2026-11-09**

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
├── modules/                         # 15 independent on-demand files
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

- Full specification: **15 modules**, with core decision workflows operating offline and external integrations explicitly tracked as partial or `not-implemented`.
- Language: **fa / en supported**; other languages require a locale file, registry change, and regression tests. English-only upstream Hook scores are **not validated for Persian**.
- Source provenance: **41 byte-identical files from six GitHub repositories** in the development repo; **21 selected source files** ship inside the installed Skill. Original MIT/Apache-2.0 licenses are retained. `docs/UPSTREAM_SOURCE_MANIFEST.json` and the installed `references/source-attribution.json` record source commit SHA and import date.
- Live Instagram OAuth/Insights, store API sync, real publishing and paid-ad execution remain **not-implemented**. Media-generation and paid-ad integrations are **optional and disabled** until explicitly authorized.
- CI: Python/unit/contract tests **and a real Skills CLI installation smoke test**. Fixed bilingual agent behavior fixtures are in `evals/`; actual LLM-generated response evaluation is **not executed** in this environment and must not be confused with code tests.

See [implementation status](skills/instagram-brand-director/references/implementation-status.json), [change log](CHANGELOG.md), [agent eval fixtures](evals/agent-scenarios.json) and [release checklist](docs/RELEASE_CHECKLIST_FA.md).

## Reference projects

[social-media-skills](https://github.com/social-media-skills/skills) · [Jake Instagram Agent Skill](https://github.com/Jakeschincariol/instagram-agent-skill) · [Instagram Skills](https://github.com/sergebulaev/instagram-skills) · [Marketing Skills](https://github.com/coreyhaines31/marketingskills) · [Digital Marketing Skills](https://github.com/vidual-labs/digital-marketing-skills) · [Apify Awesome Skills](https://github.com/apify/awesome-skills).

