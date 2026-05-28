# Submitting to the DiffSpot Leaderboard

DiffSpot uses an **offline** submission flow (no automated CI scoring). You run your
model on the dataset, then get it scored in one of two ways:

- **Option A — Self-evaluate and report.** You run the official LLM judge yourself and
  open a PR with both your raw predictions and the resulting scores. We spot-check the
  numbers before merging.
- **Option B — Send predictions, we score.** You open a PR (or email us) with only your
  raw predictions; a maintainer runs the official judge and fills in the scores.

Either way, **the submission must include raw predictions** (not scores alone) so the
judge can be re-run against the locked judge prompt for verification.

## Step 1 — Run your model

Use one of the provided baseline runners as a template:

- API-hosted models: [`baselines/api/`](../baselines/api/)
- Self-hosted models: [`baselines/local/`](../baselines/local/)

Use the prompts in [`diffspot/prompts/`](../diffspot/prompts/) **verbatim**. Submissions
that modify the prompts are not eligible for the official leaderboard (you may still
report them as an unofficial result in your own paper).

Output: a predictions JSONL with the schema documented in [`evaluation.md`](evaluation.md).

## Step 2 — Validate the predictions file

```bash
python scripts/prepare_submission.py \
    --predictions results/<your-model>/predictions.jsonl \
    --output submissions/<your-model>.zip
```

This checks coverage (all 4,400 items present), schema, and a consistent prompt version.

## Step 3 — Score

### Option A: self-evaluate

```bash
export OPENAI_API_KEY=...        # judge endpoint key
# export OPENAI_BASE_URL=...     # if the judge runs on a vLLM/sglang/gateway endpoint

python scripts/evaluate.py \
    --predictions results/<your-model>/predictions.jsonl \
    --judge-model gpt-oss-120b \
    --output results/<your-model>/scores.json

python scripts/show_results.py results/<your-model>/scores.json
```

Include the produced `scores.json` in your PR. We re-run the judge to confirm before merging.

### Option B: let us score

Skip the judge step. Submit only `predictions.jsonl` (Step 4); a maintainer runs
`scripts/evaluate.py` with the official judge and produces `scores.json`.

## Step 4 — Open a PR

1. Fork the repo.
2. Add `results/<your-model>/predictions.jsonl` (raw model outputs). For Option A, also add `results/<your-model>/scores.json`.
3. Add `results/<your-model>/README.md` with:
   - Model card / paper / open-weight URL
   - Sampling parameters (temperature, top_p, max_tokens, etc.)
   - Hardware (for self-hosted)
   - Total cost / wall-clock if known
4. Open a PR titled `[leaderboard] Add <your-model>`.

(No GitHub credentials? Email the predictions to the maintainers — contact in the paper — and we handle the PR.)

## How the leaderboard is updated

Once a submission is verified, a maintainer adds the entry to
[`leaderboard/leaderboard.json`](../leaderboard/leaderboard.json) and regenerates the
leaderboard figure shown in the README. The leaderboard is maintainer-curated; there is
no automated CI scoring step.

## Closed-source models

If your model is only available behind a private API, you can still submit by:

1. Running it yourself and uploading raw predictions (preferred — lets the community verify), or
2. Providing temporary inference access to a maintainer (contact in the paper).

Score-only submissions are not accepted: we need raw predictions so the judge can be re-run against the locked judge prompt.
