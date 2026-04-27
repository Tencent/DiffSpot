# Results

Per-model raw predictions and scores. Two purposes:

1. **Reproducibility** — anyone can re-run `scripts/evaluate.py` against these JSONLs and reproduce the leaderboard numbers without paying for inference
2. **Secondary analysis** — the predictions are structured so researchers can do per-mutation, per-domain, and cross-model error analysis without rerunning anything

## Layout per model

```
results/<model-id>/
├── README.md          # Model card: source, hardware, params, cost, links
├── predictions.jsonl  # Raw model outputs (one line per dataset item)
└── scores.json        # Judge-aggregated metrics (computed by CI)
```

## Naming

Use the lowercase model identifier with hyphens:

- `gpt-5.4`
- `claude-opus-4-6`
- `gemini-3.1-pro`
- `qwen3-vl-235b-a22b`
- `kimi-k2.5`
- `glm-4.6v`

## Initial release

The release will ship with predictions for the models reported in the paper. Community contributions are welcome — see [`docs/submission.md`](../docs/submission.md).
