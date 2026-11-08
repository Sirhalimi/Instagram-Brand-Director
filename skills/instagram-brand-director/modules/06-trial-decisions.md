# Trial Reels, content format and post-test decisions

**Scope:** Instagram Brand Director module 06

**Reference implementations:** Original: campaign_decision.py/trial_review.py; J: ig-audit; official Meta Trial guidance. Source materials are preserved under repository `third_party/` or referenced in `references/source-attribution.md`; only selected vetted tools ship with the installed Skill.

## Load this module when
Requests concern trial reels, content format and post-test decisions; do not load other modules unless the task requires their data or permissions.

## Procedure
1. Before posting, assess objective, novelty, urgency, current audience relevance, feature availability in this account, creative rights and verified commercial preflight.
2. Choose one definite next action: TRIAL_REEL, NORMAL_REEL, CAROUSEL, REWORK, PAUSE or REQUEST_CRITICAL_DATA. Treat requests for Trial as platform-specific features, not API permissions.
3. When Trial is chosen, obtain owner approval and use a supported native interface unless an authorized integration has been tested; mark exact publication time.
4. Review at brand-agreed windows (typically first ~24h and again at ~72h). **Predeclared brand policy defaults:** at least 300 reach on the Trial, at least 6 independent comparable historical posts, at least 1800 pooled historical reach, comparable format/objective/window and valid first-party metrics. If any gate fails, return `INSUFFICIENT_DATA` EVEN AFTER 72 HOURS. Never label low-reach Trial as a failure or success just because the clock expired. Use `scripts/trial_review.py`.
5. After results, decide SHARE_WITH_EVERYONE, KEEP_TESTING, REWORK or NO_CONCLUSION and log reasons and data **only as single observations**. A single high-performing Reel can motivate a one-off operational action, but never proves a repeatable content formula. Read `knowledge/learnings-governance.md` before proposing memory updates.

## Output
One distribution decision plus review trigger and rejection rationale.

## Guardrails and implementation gaps
Trial performance isn't guaranteed and Instagram weights are not public. Never pretend the tool can toggle Trial through API without proof.

## Language and evidence
Write in the brand's preferred locale (currently `fa` or `en`); preserve exact product names and numeric data. All public Meta claims must be checked against `../knowledge/instagram-rules.md` and dated sources. Missing metrics are unknown, never invented. Use `../references/response-contracts.md` for the response appropriate to the request.
