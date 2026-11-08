# Instagram Brand Director

**Version:** v0.4 specification / GitHub bootstrap (2026-11-08)

An evidence-driven, brand-adaptive social media and marketing director Agent Skill for Instagram. It chooses one actionable next step, challenges poor marketing assumptions, and prioritizes commercial viability over vanity metrics.

> **Publication status:** This GitHub repository currently contains the published skill specification and project documentation. The previously prepared local v0.4 bundle includes additional scripts, templates, module references and 44 local tests, but those components are **not yet fully mirrored to this GitHub repository**. Do not mistake a capability being listed for a working integration.

## Install

Compatible Agent Skills clients may load this repository's `SKILL.md`. For the Skills CLI, inspect current support for your agent and run:

```bash
npx skills add Sirhalimi/Instagram-Brand-Director
```

If using an agent without a repository installer, clone this repo and point its skill directory at `SKILL.md`.

## Start using it

Ask: “Act as Instagram Brand Director for my brand. Interview me briefly about brand identity, current problems, products, stock, prices, target audience, and production constraints. Give me a single prioritized marketing decision with reasoning and a review criterion.”

## Core coverage

Brand onboarding; audience research; profile and performance audits; competitor research; content strategy and calendar; Reels, Trial Reels, Carousels and Stories; Instagram SEO and organic growth; community management; catalog/stock/margin-aware promotion; sales funnels; publishing preflight and approval; metrics, experimentation and learning; current Meta policies and grounded critical feedback.

**Optional, disabled until configured:** generated image/video/audio integrations and actual paid-ad campaign execution. Content strategy and advertising advice remain available without these integrations.

## Decision principles

- A decisive recommendation is not a promised outcome.
- Never recommend promoting a sold-out or unverifiably deliverable product.
- Never silently recommend face-to-camera formats if the brand cannot make them.
- Never invent Instagram Insights, audience demographics, pricing, competitor sales or algorithm weights.
- Never publish, DM, spend advertising budget or change an account without explicit approval.
- Prefer official Meta APIs where supported; CSV/manual exports otherwise. An installed skill alone cannot authorize an account.

## Source credits

Derived from independent analysis of [Social Media Skills](https://github.com/social-media-skills/skills), [Instagram Agent Skill](https://github.com/Jakeschincariol/instagram-agent-skill), [Instagram Skills](https://github.com/sergebulaev/instagram-skills), [Marketing Skills](https://github.com/coreyhaines31/marketingskills), [Digital Marketing Skills](https://github.com/vidual-labs/digital-marketing-skills) and [Apify Awesome Skills](https://github.com/apify/awesome-skills). Licensed upstream files are now included under `third_party/` (Jake Instagram Agent Skill, Social Media Skills, sergebulaev Instagram Skills, and vidual-labs Digital Marketing Skills). See `docs/UPSTREAM_COMPARISON_2026_11_FA.md` for files, caveats and integration status.

## Executable components currently in GitHub

- `scripts/catalog_guard.py`: commercial preflight for product stock, fulfillment, price freshness and campaign margin policy.
- `scripts/trial_review.py`: offline post-Trial comparison against the account's configured baseline.
- `scripts/campaign_decision.py`: decisive format and campaign recommendation combining brand production constraints, creative rights, account Trial availability and catalog checks.
- `tests/`: 29 regression tests for these three GitHub components; GitHub Actions runs the suite on pushes and pull requests.
- `examples/`: synthetic JSON inputs. No real account, customer data or API tokens are included.

Try the campaign decision engine:

```bash
python3 -m scripts.campaign_decision examples/campaign-brief.sample.json
python3 -m scripts.trial_review examples/trial-review.sample.json
python3 -m unittest discover -s tests -v
```

These scripts **do not** connect accounts, publish posts, run paid advertisements or access live inventories. They choose auditable actions from the data supplied to them. Selected upstream tools have been imported with source licenses and smoke tests. The full original local v0.4 bundle has not yet been mirrored to GitHub.

## Development priorities

1. Mirror the remaining original v0.4 source bundle and local tests into GitHub, reconciling against already-imported upstream tools.
2. Integrate a full product catalog and fresh stock/cost data adapters.
3. Complete Meta OAuth and read-only Insights validation.
4. Complete dependency closure for copied upstream skills and develop Persian-specific tests/adapters; English-oriented tools have already been imported and smoke-tested.
5. Add CI and clear operational release/version gates.
6. Implement publishing connectors only where the permissions and human approval workflow are proven.

See `docs/FEATURE_SCOPE_FA.md` for Persian module scope and `docs/DEPLOYMENT_STATUS.md` for live status.
