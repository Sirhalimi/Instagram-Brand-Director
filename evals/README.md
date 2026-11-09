# Agent behavior evaluation fixtures / سناریوهای رفتار ایجنت

The ten legacy aggregated fixtures in evals/agent-scenarios.json define expected behavior in Persian and English. Six **additional** independent phase-5 scenarios under tests/behavior/ add account-state and goal-conflict coverage. They cover sold-out promotions, faceless brands, camera onboarding, unreasonable owner instructions, compact caption output, Trial evidence gaps, and Meta source checking.

**Two distinct validation levels:**

1. `python3 -m unittest discover -s tests -v` runs **deterministic contract tests** against the shipped routing probe and offline decision engines. It confirms decision codes, why/action fields and file budgets. This is not a language model generating a response.
2. **Optional Codex CLI behavior evaluation runner exists but has NOT been executed against a live model.** From the repository root: `python3 tools/run_agent_eval.py --mode prepare --output /tmp/igbd-prep` safely stages all cases with no API calls. With an independently authenticated Codex CLI, opt in explicitly: `python3 tools/run_agent_eval.py --mode run --case fa_sold_out --output /tmp/igbd-live --allow-model-usage`. A one-case, manual-only GitHub Actions workflow is also provided; it requires `OPENAI_API_KEY` configured as a repository secret. Each run captures the agent response and event stream; all outputs require independent human grading. Automatic keyword screening is too weak to certify behavior.

## Pass criteria for actual agent eval
- Out-of-stock product: states `DO_NOT_PROMOTE` or an equivalent clear rejection, explains the business harm and gives a feasible alternative.
- Faceless brand: never proposes a talking-head Reel or forces on-camera filming.
- Camera preference unknown: asks before writing a specific on-camera production plan.
- Weak instruction: respectfully disagrees and does not optimize a vanity metric over unsatisfied customers.
- Caption-only request: finished caption appears before strategy, with minimal extra material.
- Trial with 1–2 posts or low reach: explicitly **insufficient evidence**, no claimed failure/success pattern and no `learnings.md` write.
- Route budget: ordinary prompt should load router + primary module only. Multi-objective requires at most two modules, with knowledge only if a platform-specific claim is made.

## Agent eval record template
`{fixture_id, agent_version, model, tested_at, actual_response, files_loaded, decision, compliance_result, reviewer_note}`

Re-run behavior evaluation on every release that changes routing, response contracts, Trial sampling policy or localized copy rules. Do not put brand secrets in fixtures; these are synthetic examples.

**Important:** Official `skill-creator` guidance provides a quick structure validator but does not itself establish that these model-output scenarios passed. We deliberately distinguish skill structure lint, deterministic engine tests, and actual agent response evaluation.

## Phase 5 independent scenario directory

Run `python3 tools/run_agent_eval.py --mode prepare --fixtures tests/behavior --output /tmp/igbd-phase5-prep`. This never executes a model. Every fixture has its own independent rubric.json outside the model workspace, with expectations/forbidden outcomes withheld from prompt.txt. To deliberately evaluate one case using a configured Codex CLI: `python3 tools/run_agent_eval.py --mode run --fixtures tests/behavior --case phase5_sold_out_fa --allow-model-usage --output /tmp/igbd-phase5-live`. This may use paid credits; ALL actual response judgments require human review. For phase-5 cases the program deliberately reports `NOT_GRADED` rather than a lexical 'pass'. Read docs/BEHAVIOR_EVAL_PHASE5_FA.md.
