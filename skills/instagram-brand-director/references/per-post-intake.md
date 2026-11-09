# Per-post intake and optional durable preferences

The installed Skill has `scripts/post_intake.py`. It is **read-only by default** and needs only explicit private files. It does not authenticate, use a network, or read credentials.

```bash
python3 -m scripts.post_intake --brand /private/brands/demo/brand.md --post /private/brands/demo/current-post.json
python3 -m scripts.post_intake --brand /private/brands/demo/brand.md --post /private/brands/demo/current-post.json --answers /private/brands/demo/post-answers.json --save
```

Answers format (synthetic illustration): `{"answers":{"post_goal":"saves","target_audience":"students studying chemistry"},"durable_keys":["target_audience"]}`. With `--save`, **only** keys listed in `durable_keys` are persisted inside `brand.md` under `post_defaults`; ephemeral shoot choices remain in the post brief. This is an explicit owner-approved action that updates the exact supplied brand file atomically. Do not commit the brand folder.

Post intake checks **only unknown** answers: camera presenter for video if not already confirmed faceless, exact intended audience, excluded audience, post goal (trust/saves/sends/leads/sales), production capacity. If existing broad `brand.target_audience` is a real target rather than the template placeholder, it is reused; more precise post targeting may override it. `primary_goal` (discovery/conversion/education/community) is not silently converted into the separate per-post goal enumeration.

Pure captions must not be blocked by on-camera questions or forced strategic memoranda. For brand strategy, account-state preflight comes first. The intake and router scripts are deterministic probes; actual agent output still needs separate LLM evaluation.
