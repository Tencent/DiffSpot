# Prompt Design Notes

The DiffSpot prompts in [`diffspot/prompts/`](../diffspot/prompts/) are versioned and pinned. This document explains why they are written the way they are.

## VLM prompts (vlm_diff.txt, vlm_nodiff.txt)

Both prompts are **identical in wording**. This is deliberate.

### Why identical?

If the has-diff prompt asserted "Some subtle changes have been made..." while the no-diff prompt said "These two screenshots may or may not differ...", the model's prior over "is there a change?" would diverge between the two tracks, biasing the hallucination metric upward.

### Why "may have been made" instead of "have been made"?

Earlier iterations used the assertive form ("Some subtle changes have been made"). On no-diff pilot runs (500 items per model), this produced systematically inflated hallucination rates — Qwen3-VL-30B-Instruct at 51.6%, Kimi-K2.5 at 28.2%, Gemini 3 Flash at 28.0%. The assertive form primes the model to report _something_, even when nothing changed.

The released v1.0 prompt uses the possibility form ("Subtle changes may have been made") so that no-diff items are evaluated under the same prior as has-diff items.

### Format requirements

- Bullet points, one per difference
- Each bullet must specify (a) which element, (b) what changed, (c) direction/magnitude
- Explicit "no differences observed" output is allowed and treated as zero reported diffs

## Judge prompt (judge.txt)

Locked at v1.0. Reproduced verbatim in the paper appendix.

The judge takes:
- The GT mutation list (operator + element + before/after values)
- The GT natural-language description
- The model's prediction

And outputs strict JSON (`matched_gt`, `reported_diffs`, `correct_reports`, `any_change_reported`).

The judge is `gpt-oss-120b` with `temperature=0` and `reasoning_effort=high`. We measured judge agreement on a 200-item human-labeled subset; agreement numbers are in the paper.

## Modifying prompts

Any change to the prompts breaks comparability with the released leaderboard:

- **Acceptable**: experiment with prompts in your own paper, clearly labeled as a non-official run
- **Not acceptable**: submit modified-prompt predictions to the official leaderboard
- **Process for upgrading the official prompts**: bump `JUDGE_VERSION` (or define a `PROMPT_VERSION` for the VLM prompts), publish a v2 dataset revision, re-run all baselines, and document the change in `CHANGELOG.md`
