# Evaluation Protocol

## Inputs

- 4,400 (image_a, image_b) screenshot pairs (3,900 has-diff + 500 no-diff)
- Two prompt files in [`diffspot/prompts/`](../diffspot/prompts/):
  - `vlm_diff.txt` — used for has-diff items
  - `vlm_nodiff.txt` — used for no-diff items
- The two VLM prompts are intentionally **identical in wording** to keep the prior over "is there a change?" the same in both tracks. Any divergence biases the hallucination metric.

## Output format (per model)

A single JSONL with one record per dataset item:

```json
{
  "id": "...",
  "split": "easy" | "medium" | "hard" | "no_diff",
  "model": "...",
  "prompt_version": "v1.0",
  "raw_response": "...",
  "prediction": "..."
}
```

## Metrics

DiffSpot reduces each pair to a binary judgment (model identified the GT mutation? / model claimed any change on a no-diff page?), then aggregates as follows.

### Has-diff items (`easy` / `medium` / `hard`)

The LLM judge marks, for each pair, whether the model's free-form prediction matched the structured GT mutation (`correct` / `partial` / `missed` per the v2.0 judge schema; `correct` counts as a true positive).

- **Easy Recall** = TPs / 1,300 — fraction of Easy has-diff pairs where the model identified the mutation
- **Med Recall** = TPs / 1,300
- **Hard Recall** = TPs / 1,300
- **Diff Overall Recall** = TPs / 3,900

### No-diff items (`no_diff` split)

- **No-Diff Specificity** = TNs / 500 — fraction of no-diff pairs where the model reported _no_ change

### Headline metric

- **Overall Accuracy** = (TP + TN) / 4,400 — official leaderboard score
  - TP from the 3,900 has-diff pairs (model correctly identified the mutation)
  - TN from the 500 no-diff pairs (model correctly reported no change)
- Trivial baselines: always-no-diff = 11.4% Accuracy (= 500/4,400)

### Optional per-mutation breakdown

- Per-operator Recall on the 13 mutation operators (300 pairs per operator across the three difficulty tiers)
- Reported in the paper's analysis section, not the headline leaderboard

## Judge

- Model: `gpt-oss-120b`
- Settings: `temperature=0`, `reasoning_effort=high`
- Prompt: pinned at [`diffspot/prompts/judge.txt`](../diffspot/prompts/judge.txt) (`JUDGE_VERSION=v2.0`)
- The exact judge prompt is reproduced in the paper appendix.

## Reproducibility

- Pin `--dataset-revision <commit_sha>` to lock the exact data version
- Use `--max-tokens 16384` minimum for any thinking-style model (otherwise reasoning will eat the output budget and `content` returns empty)
- Use `temperature=0` for both VLM and judge to minimize variance

## Reporting

When citing DiffSpot results, please report **at minimum** these six numbers per model:

1. Easy Recall (1,300 pairs)
2. Med Recall (1,300 pairs)
3. Hard Recall (1,300 pairs)
4. Diff Overall Recall (3,900 pairs)
5. No-Diff Specificity (500 pairs)
6. **Overall Accuracy** (the headline leaderboard score)

Reporting Recall alone without Specificity is misleading — a model that aggressively over-reports diffs can inflate Recall on has-diff pairs while being unusable in practice (it will hallucinate on no-diff pages too). The Overall Accuracy combines both into a single per-case binary metric.
