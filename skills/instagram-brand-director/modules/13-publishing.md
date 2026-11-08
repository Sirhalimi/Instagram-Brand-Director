# Publication approval, scheduling and QA

**Scope:** Instagram Brand Director module 13

**Reference implementations:** S: scheduling-and-queue, platform-specs; I: ig-caption-writer (approval flow). Source materials are preserved under repository `third_party/` or referenced in `references/source-attribution.md`; only selected vetted tools ship with the installed Skill.

## Load this module when
Requests concern publication approval, scheduling and qa; do not load other modules unless the task requires their data or permissions.

## Procedure
1. Check media specs and rights, source integrity, branded claims, captions, verified product offers, language, alt text and required disclosures.
2. Present final approved payload and record content hash, reviewer and account identifier; any later change invalidates approval.
3. Offer the next safe action, such as native publication; schedule only through proven authorized integration and avoid unsupported Trial switches.
4. After publication, capture post ID, timestamp, platform confirmation and baseline metrics. Failure to receive confirmation is not success.
5. Before removal or paid spend, require a separate explicit confirmation.

## Output
Approval checklist and status (draft/awaiting-approval/ready/manual-publish).

## Guardrails and implementation gaps
Publishing/scheduling integrations: not-implemented; do not invent a successful publish.

## Language and evidence
Write in the brand's preferred locale (currently `fa` or `en`); preserve exact product names and numeric data. All public Meta claims must be checked against `../knowledge/instagram-rules.md` and dated sources. Missing metrics are unknown, never invented. Use `../references/response-contracts.md` for the response appropriate to the request.
