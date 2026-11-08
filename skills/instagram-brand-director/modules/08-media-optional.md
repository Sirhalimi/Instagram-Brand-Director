# Media-generation service integrations — optional

**Scope:** Instagram Brand Director module 08

**Reference implementations:** S: image-prompt, ai-video, canva, capcut, flux, ideogram, veo, runway. Source materials are preserved under repository `third_party/` or referenced in `references/source-attribution.md`; only selected vetted tools ship with the installed Skill.

## Load this module when
Requests concern media-generation service integrations — optional; do not load other modules unless the task requires their data or permissions.

## Procedure
1. Core creative brief and shot list always work without an external service. Treat actual image/video/audio generation as optional, disabled by default.
2. If enabled by a specific user, select a compatible approved service for budget and rights; confirm available credentials outside chat and understand its privacy terms.
3. Develop production prompts and human edit checkpoints; store generated assets with rights metadata in the brand workspace, not public repo.
4. Before release check visual accuracy, product likeness, disclosure obligations, subtitles, resolution, safe zones and licenses.
5. When disabled, provide an executable production plan using physical photos, templates or existing assets.

## Output
Optional production assets or tool-independent creative brief.

## Guardrails and implementation gaps
Status of actual service adapters: not-implemented. Never claim a provider account is connected.

## Language and evidence
Write in the brand's preferred locale (currently `fa` or `en`); preserve exact product names and numeric data. All public Meta claims must be checked against `../knowledge/instagram-rules.md` and dated sources. Missing metrics are unknown, never invented. Use `../references/response-contracts.md` for the response appropriate to the request.
