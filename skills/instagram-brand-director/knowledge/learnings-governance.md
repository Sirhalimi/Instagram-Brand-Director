# Learnings governance — EN / FA

- Treat metrics from one or two posts as **observations**, not actionable patterns.
- A Trial with fewer than 6 comparable historical posts, 1800 pooled baseline reach, or 300 Trial reach (default *brand-configured* floors) must return `INSUFFICIENT_DATA`, even after 72 hours.
- A single Trial with enough samples may support a **one-off operational action**, never a claim that a creative formula consistently works.
- Before adding content to private `learnings.md`, require repeated independent posts (default minimum 4), a pooled minimum of 3000 reach and 300 reach per post, aligned format/goal/period, same predeclared hypothesis, no unresolved confounders, and human approval. These are **conservative internal guardrails**, not official Instagram thresholds or statistical guarantees.
- The script `scripts/learning_gate.py` **never writes** `learnings.md`, even when sample conditions pass. It only marks evidence as a candidate for manual critical review.
- Store data provenance, dates, alternate explanations, confidence, and reversal condition for any approved learning. Use `observations.md` for weak signals; never rewrite history post hoc.
