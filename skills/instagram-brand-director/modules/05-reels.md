# Reels creative production

**Scope:** Instagram Brand Director module 05

**Reference implementations:** J: ig-reel/hookscore.py/beats.py/hooks.json; S: reels-script. Source materials are preserved under repository `third_party/` or referenced in `references/source-attribution.md`; only selected vetted tools ship with the installed Skill.

## Load this module when
Requests concern reels creative production; do not load other modules unless the task requires their data or permissions.

## Procedure
1. Load brand voice and creative constraints first. **If camera preference is unknown, ask one direct question before drafting a shooting plan: can/will anyone appear on camera?** Do not force on-camera content; for a confirmed no-face brand use only faceless options. Choose one promise that can be substantiated and produced.
2. Write three genuinely different hook concepts; ensure first frame/on-screen text works without audio where relevant.
3. For English: run copied upstream hookscore.py and beats.py only as editing heuristics; for Persian: run `python3 -m scripts.creative_quality hook --text ...`, no English score or view forecast.
4. Create beat sheet: hook, stakes, main value, payoff, CTA, shot, on-screen text, spoken/audio, timing, accessibility captions and cover. If no camera: product shots, b-roll, animation or text-led Reel.
5. Check rights, originality, accuracy, music licensing, accessibility and brand limits; route distribution choice to module 06.

## Output
Shootable Reel brief and script with one action-ready recommendation.

## Guardrails and implementation gaps
No forced face-to-camera, no fabricated results or precise watch-time algorithm weights.

## Language and evidence
Write in the brand's preferred locale (currently `fa` or `en`); preserve exact product names and numeric data. All public Meta claims must be checked against `../knowledge/instagram-rules.md` and dated sources. Missing metrics are unknown, never invented. Use `../references/response-contracts.md` for the response appropriate to the request.
