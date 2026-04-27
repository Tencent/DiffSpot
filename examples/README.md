# Examples

Once the dataset is published on HuggingFace, this directory will contain:

- `walkthrough.ipynb` — load a few items, run a baseline, score with the judge
- `sample_predictions.jsonl` — 10 example predictions per split (with judge labels)
- `sample_screenshots/` — 5 (image_a, image_b) pairs covering different mutation types

Until then, see [`tests/`](../tests/) for self-contained unit tests of the metrics aggregator and the judge prompt renderer that exercise the same code paths without needing real data or API access.

## Running the existing tests

```bash
pip install -e ".[dev]"
pytest -v tests/
```

This will:

- Verify `diffspot.metrics.aggregate()` reproduces the Gemini 3.1 Pro main-table numbers (47.2% Overall) from synthetic per-item labels
- Verify the judge prompt template's brace-escaping logic (the v2.0 prompt's literal output schema must round-trip unchanged)
- Verify `leaderboard/update.py` correctly renders / sorts / bolds the leaderboard table

No network calls; no API keys; no dataset download.
