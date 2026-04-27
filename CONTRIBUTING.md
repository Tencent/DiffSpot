# Contributing to DiffSpot

Thanks for considering a contribution. The most common contribution to a benchmark is **a new baseline on the leaderboard**; the second most common is **bug reports / fixes** in the eval pipeline.

## Adding a baseline to the leaderboard

See [`docs/submission.md`](docs/submission.md) for the full flow. Short version:

1. Use one of the runners in [`baselines/`](baselines/) as a template
2. Generate a predictions JSONL using the **canonical prompts** in [`diffspot/prompts/`](diffspot/prompts/) — the official leaderboard requires verbatim use of the v1.0 VLM prompts and v2.0 judge prompt
3. Validate: `python scripts/prepare_submission.py --predictions <file> --output submission.zip`
4. Open a PR adding `results/<your-model>/predictions.jsonl` and a `results/<your-model>/README.md` documenting the model card, sampling params, hardware, and total cost
5. CI will re-run the official judge and update the leaderboard

## Bug reports

Please include:

- Python version, OS, `pip freeze | grep -E "openai|anthropic|datasets|diffspot"`
- The exact command you ran
- Full stack trace
- Whether the issue is in eval (`scripts/evaluate.py`), a baseline runner, or the metrics

For metrics or judge bugs, attach the smallest predictions JSONL that reproduces.

## Code changes

- `pip install -e ".[dev]"` to set up
- `ruff check diffspot/ baselines/ scripts/ leaderboard/ tests/` before pushing
- `pytest -v tests/` — all tests must pass
- Keep changes focused; do not bundle prompt edits with code refactors

## Modifying prompts

Any change to a prompt in [`diffspot/prompts/`](diffspot/prompts/) breaks comparability with the released leaderboard.

- **Acceptable in your own paper / fork**: clearly labeled as a non-official run
- **Not acceptable for the official leaderboard**: PR will be rejected
- **Process for upgrading the official prompts**: bump `JUDGE_VERSION` (or define a `PROMPT_VERSION` for the VLM prompts), publish a new dataset revision, re-run all baselines, and document the change in `CHANGELOG.md`

## Code of conduct

Be excellent to each other. Discriminatory, harassing, or hostile behavior is not tolerated and will result in PR / issue closure and a ban from the repository.
