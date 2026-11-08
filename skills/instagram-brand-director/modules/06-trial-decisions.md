# Trial Reels, content format and post-test decisions

**Scope:** Instagram Brand Director module 06

**Reference implementations:** Original: campaign_decision.py/trial_review.py; J: ig-audit; official Meta Trial guidance. Source materials are preserved under repository `third_party/` or referenced in `references/source-attribution.md`; only selected vetted tools ship with the installed Skill.

## Load this module when
Requests concern trial reels, content format and post-test decisions; do not load other modules unless the task requires their data or permissions.

## Procedure
1. Before posting, assess objective, novelty, urgency, current audience relevance, feature availability in this account, creative rights and verified commercial preflight.
2. Choose one definite next action: TRIAL_REEL, NORMAL_REEL, CAROUSEL, REWORK, PAUSE or REQUEST_CRITICAL_DATA. Treat requests for Trial as platform-specific features, not API permissions.
3. When Trial is chosen, obtain owner approval and use a supported native interface unless an authorized integration has been tested; mark exact publication time.
4. Review at brand-agreed windows (typically first ~24h and again at ~72h) against comparable first-party baseline with sample thresholds declared beforehand. Use trial_review.py.
5. After results, decide SHARE_WITH_EVERYONE, KEEP_TESTING, REWORK or STOP and log reason, data and review date.

## Output
One distribution decision plus review trigger and rejection rationale.

## Guardrails and implementation gaps
Trial performance isn't guaranteed and Instagram weights are not public. Never pretend the tool can toggle Trial through API without proof.

## Language and evidence
Write in the brand's preferred locale (currently `fa` or `en`); preserve exact product names and numeric data. All public Meta claims must be checked against `../knowledge/instagram-rules.md` and dated sources. Missing metrics are unknown, never invented. Use `../references/response-contracts.md` for the response appropriate to the request.
