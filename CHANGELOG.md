# Changelog

All notable changes to the DiffSpot benchmark and evaluation code.

## [Unreleased]

- Initial repository skeleton. Dataset, baselines, leaderboard, and Space pending public release alongside the paper.

## [v1.0] — TBD

- 4,400 evaluation instances (1,300 easy + 1,300 medium + 1,300 hard + 500 no-diff)
- 13 CSS-property-level operators in 4 families (typography / color / layout / shape)
- 39 balanced cells (13 operators × 3 difficulty tiers × 100 pairs)
- LLM-as-Judge prompt v2.0 (`gpt-oss-120b`, `reasoning_effort=high`)
- 13 reference baselines (4 proprietary + 9 open-weight)
- Headline metric: per-case Overall Accuracy = (TP+TN)/4,400
