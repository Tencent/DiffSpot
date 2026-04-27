# Submitting to the DiffSpot Leaderboard

DiffSpot uses an offline submission flow: you run your model on the public dataset, generate a predictions JSONL, and open a PR with the file. We re-run the official judge in CI and update the leaderboard.

## Step 1 — Run your model

Use one of the provided baseline runners as a template:

- API-hosted models: [`baselines/api/`](../baselines/api/)
- Self-hosted models: [`baselines/local/`](../baselines/local/)

Required: use the prompts from [`diffspot/prompts/`](../diffspot/prompts/) **verbatim**. Submissions that modify the prompts will be rejected from the official leaderboard but can still be reported in your own paper as an unofficial result.

Output: a JSONL with the schema documented in [`evaluation.md`](evaluation.md).

## Step 2 — Validate

```bash
python scripts/prepare_submission.py \
    --predictions results/<your-model>/predictions.jsonl \
    --output submissions/<your-model>.zip
```

This checks coverage (all 4,400 items present), schema, and prompt version.

## Step 3 — Open a PR

1. Fork the repo
2. Add your predictions under `results/<your-model>/predictions.jsonl` (raw model outputs, not scores — scores are computed in CI)
3. Update `results/<your-model>/README.md` with:
   - Model card / paper / open-weight URL
   - Sampling parameters (temperature, top_p, max_tokens, etc.)
   - Hardware (for self-hosted)
   - Total cost / wall-clock if known
4. Open a PR titled `[leaderboard] Add <your-model>`

## What CI does

1. Re-runs `scripts/evaluate.py` with the official judge
2. Writes `results/<your-model>/scores.json`
3. Runs `leaderboard/update.py` to refresh the README table
4. Posts the resulting numbers as a PR comment for review

## Closed-source models

If your model is not publicly accessible, you can still submit by:

1. Running it yourself and uploading raw predictions (preferred; lets the community verify)
2. Or providing inference access to one of the maintainers (contact: TBD)

We cannot accept score-only submissions — only raw predictions, so the judge can be re-run against the locked judge prompt.
