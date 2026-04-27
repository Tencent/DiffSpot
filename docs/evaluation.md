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

### Has-diff items (`easy` / `medium` / `hard`)

For each item, the LLM judge produces:

- `matched_gt`: which GT mutations were correctly identified by the model
- `correct_reports`: which of the model's reported diffs match a GT mutation

Per-item:

- `Recall    = |matched_gt| / |GT|`
- `Precision = |correct_reports| / |reported_diffs|`  (Precision = 1 if no reports)
- `F1`       = harmonic mean

Aggregated metrics:

- **Diff F1 (split)**: macro-average of per-item F1 within each split
- **Diff F1 (overall)**: macro-average across all has-diff items
- **Per-mutation Recall**: per-operator recall (12 operators)

### No-diff items (`no_diff` split)

- **Hallucination Rate** = fraction of no-diff items where the model reported any change

## Judge

- Model: `gpt-oss-120b`
- Settings: `temperature=0`, `reasoning_effort=high`
- Prompt: pinned at [`diffspot/prompts/judge.txt`](../diffspot/prompts/judge.txt) (`JUDGE_VERSION=v1.0`)
- The exact judge prompt is reproduced in the paper appendix.

## Reproducibility

- Pin `--dataset-revision <commit_sha>` to lock the exact data version
- Use `--max-tokens 16384` minimum for any thinking-style model (otherwise reasoning will eat the output budget and `content` returns empty)
- Use `temperature=0` for both VLM and judge to minimize variance

## Reporting

When citing DiffSpot results in a paper, please report **all four** numbers per model:

1. Diff F1 (Easy)
2. Diff F1 (Medium)
3. Diff F1 (Hard)
4. Hallucination Rate

Reporting Diff F1 alone without the hallucination rate is misleading — a model that aggressively over-reports differences can inflate F1 on has-diff items while being unusable in practice (high false-positive rate on no-diff pages).
