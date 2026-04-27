# Baselines

Reference runners for the models reported in the DiffSpot paper. Each runner:

1. Loads the official dataset (HuggingFace, pinned by revision)
2. Calls the target model on each (image_a, image_b) pair using the canonical prompts in [`diffspot/prompts/`](../diffspot/prompts/)
3. Writes a predictions JSONL with the schema below

Predictions JSONL schema (one record per dataset item):

```json
{
  "id":         "...",
  "split":      "easy" | "medium" | "hard" | "no_diff",
  "model":      "<model identifier>",
  "prompt_version": "v1.0",
  "raw_response":   "<full raw model output>",
  "prediction":     "<post-processed string handed to the judge>"
}
```

## Layout

```
baselines/
├── api/        # API-hosted (OpenAI / Anthropic / Google / iChat gateway)
└── local/      # Self-hosted (sglang / vllm / ollama)
```

## Adding a new baseline

1. Copy `api/run_openai.py` (or `local/run_qwen3vl.py`) as a template
2. Wire your model client in the marked TODO block
3. Document any non-standard sampling parameters in the file header
4. Run on all four splits; commit the resulting predictions JSONL under `results/<your-model>/`
5. Open a PR — the CI will re-run the judge and update the leaderboard
