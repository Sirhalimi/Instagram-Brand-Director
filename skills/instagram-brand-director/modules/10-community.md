# Comments, DMs, support and community

**Scope:** Instagram Brand Director module 10

**Reference implementations:** J: ig-reply/ig-dm; S: community-management/social-selling-and-dm. Source materials are preserved under repository `third_party/` or referenced in `references/source-attribution.md`; only selected vetted tools ship with the installed Skill.

## Load this module when
Requests concern comments, dms, support and community; do not load other modules unless the task requires their data or permissions.

## Procedure
1. Categorize inbound messages: question, order inquiry, support, complaint, praise, abuse or spam.
2. Use verified product catalog, status, delivery/returns rules for factual replies; escalate sensitive claims, personal data, refund disputes and safety cases.
3. Create brand-voice replies in the requested language and obtain approval for external sends until an authorized, audited workflow is connected.
4. Organize FAQ patterns and hand off recurring complaints to operations/product rather than manipulating engagement.
5. Track response time, satisfied resolutions and conversion with privacy-safe analytics.

## Output
Response draft or queue plus escalation signal.

## Guardrails and implementation gaps
Automated DM/comment sending: not-implemented; no unsolicited bulk outreach or use of private data from other clients.

## Language and evidence
Write in the brand's preferred locale (currently `fa` or `en`); preserve exact product names and numeric data. All public Meta claims must be checked against `../knowledge/instagram-rules.md` and dated sources. Missing metrics are unknown, never invented. Use `../references/response-contracts.md` for the response appropriate to the request.
