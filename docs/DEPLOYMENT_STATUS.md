# Development status — 2026-11-09

## Verified
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

