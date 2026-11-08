# Agent behavior evaluation fixtures / سناریوهای رفتار ایجنت

These ten fixed scenarios define expected behavior in Persian and English. They cover sold-out promotions, faceless brands, camera onboarding, unreasonable owner instructions, compact caption output, Trial evidence gaps, and Meta source checking.

**Two distinct validation levels:**

1. `python3 -m unittest discover -s tests -v` runs **deterministic contract tests** against the shipped routing probe and offline decision engines. It confirms decision codes, why/action fields and file budgets. This is not a language model generating a response.
2. **Agent runtime evaluation — not-implemented / not executed here.** When an Agent Skills `skill-creator` evaluation runtime is available, feed every `prompt` and its brand context into a fresh agent session with only `skills/instagram-brand-director/` installed. Collect the actual text response and trace which files were read. Check each `agent_expectations`, not merely the decision string. Record pass/fail, model, date, agent version, files loaded and full output; manually inspect disagreements and subjective copy quality. No tool for actual model-run eval was available in this environment, so do not claim that it passed.

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
