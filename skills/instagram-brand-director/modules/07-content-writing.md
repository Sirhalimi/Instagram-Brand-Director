# Carousel, Story and caption production

**Scope:** Instagram Brand Director module 07

**Reference implementations:** J: ig-caption, ig-story, ig-carousel; I: ig-caption-writer; S: carousel-writer. Source materials are preserved under repository `third_party/` or referenced in `references/source-attribution.md`; only selected vetted tools ship with the installed Skill.

## Load this module when
Requests concern carousel, story and caption production; do not load other modules unless the task requires their data or permissions.

## Procedure
1. Pick format based on job: carousel for sequential explanation/reference, Story for existing-audience relationship, post for focused visual, Reel for short video where feasible.
2. Build carousel cover and slide-by-slide argument; Story arc with explicit interaction and privacy-safe response handling; caption with useful first line and one optional CTA.
3. Use `creative_quality.py` for Persian text; original upstream English caption tool for English. Do not borrow a fake voice or invent testimonials.
4. Use relevant keywords naturally. Recommend hashtags only when they label the topic and align with dated Instagram rules in knowledge.
5. Return the finished copy first; small quality note and approvals only if needed. Avoid 5-paragraph strategy memos for 'write a caption'.

## Output
Ready-to-review localized copy, slide structure, alt-text hints and optional variant.

## Guardrails and implementation gaps
Do not assume every caption needs hashtags or CTA. No auto-publishing.

## Language and evidence
Write in the brand's preferred locale (currently `fa` or `en`); preserve exact product names and numeric data. All public Meta claims must be checked against `../knowledge/instagram-rules.md` and dated sources. Missing metrics are unknown, never invented. Use `../references/response-contracts.md` for the response appropriate to the request.
