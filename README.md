<div align="center">

# DiffSpot

### Can VLMs Spot Fine-Grained Visual Differences in Web Interfaces?

<br>

<p>
<a href="https://huggingface.co/datasets/tencent/DiffSpot"><img src="https://img.shields.io/badge/🤗%20Dataset-tencent/DiffSpot-yellow?style=for-the-badge" alt="Dataset"></a>
&nbsp;
<a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"></a>
&nbsp;
<img src="https://img.shields.io/badge/Benchmark-4,400%20pairs-blue?style=for-the-badge" alt="Size">
</p>

<br>

<table>
<tr>
<td>
<h3>🏆 Across 13 frontier VLMs evaluated zero-shot, even the best identifies only <b>40.7%</b> of true changes — and Hard-tier recall stays below <b>23%</b> for <i>every</i> model.</h3>
</td>
</tr>
</table>

</div>

<br>

**DiffSpot** is a benchmark for **fine-grained visual change detection in real-world web interfaces**. Each example is a pair of near-identical screenshots that differ by a single programmatic CSS-level mutation; a VLM must describe **what changed**. Ground truth is recorded directly from the mutation that produced the pair.

> [!NOTE]
> The dataset is hosted on HuggingFace at [`tencent/DiffSpot`](https://huggingface.co/datasets/tencent/DiffSpot). This repository ships the full evaluation stack — judge, metrics, baseline runners, CI, and tests. The test suite (`pytest -v tests/`) exercises the eval pipeline against synthetic data, with no API key or dataset download required.

---

## ✨ Highlights

- **4,400 evaluation instances** — 3,900 has-diff pairs + 500 no-diff controls, every pair from a URL-globally-unique page
- **13 CSS-property operators** in 4 families — typography (`font_weight` / `font_size` / `letter_spacing` / `line_height` / `text`), color (`color` / `opacity` / `gradient`), layout (`position` / `spacing` / `justify`), shape (`border` / `rounded`)
- **3 difficulty tiers** (Easy / Medium / Hard) — 39 balanced cells of 100 pairs each
- **Code-driven ground truth** — mutate one CSS property, re-render, record the change; fully reproducible
- **Grounding gate** — every pair anchored to the target element's bounding box, rejecting no-effect and reflow-contamination failures
- **Open-ended description** format + **no-diff hallucination control**, scored by an **LLM-as-Judge** ([`diffspot/prompts/judge.txt`](diffspot/prompts/judge.txt))

---

## 🏆 Leaderboard

> **Visual diff detection on the full 4,400-pair benchmark** (percentages). **Easy / Med / Hard / Diff** are Recall on has-diff pairs (1,300 per tier; 3,900 total); **No-Diff** is specificity on the 500 no-diff pairs; **Overall** is per-case accuracy `(TP + TN) / 4,400` — the official score. Judge: `gpt-oss-120b`, `reasoning_effort=high` (cross-judge Kendall τ = 1.000 across gpt-oss-120b / Kimi-K2.5 / Qwen3.5-VL-397B). **Bold** = column max; sorted by Overall within each group.

<!-- LEADERBOARD START -->

| Model | Params | Easy | Med | Hard | Diff Overall | No-Diff | **Overall** |
|---|---:|---:|---:|---:|---:|---:|---:|
| _Open-weight models_ | | | | | | | |
| Kimi K2.5 | 1T / 32B | 54.2 | 36.4 | 18.6 | 36.4 | 87.2 | 42.2 |
| Qwen3.5-VL-397B | 397B / 17B | 45.1 | 31.5 | 13.7 | 30.1 | 96.6 | 37.6 |
| Qwen3-VL-235B-Thinking | 235B / 22B | 30.1 | 17.3 | 10.5 | 19.3 | 98.8 | 28.3 |
| GLM-4.6V-Flash | 9B | 24.5 | 17.6 | 9.3 | 17.1 | 75.8 | 23.8 |
| GLM-4.6V | 106B / 12B | 17.0 | 10.9 | 5.5 | 11.2 | 99.6 | 21.2 |
| Qwen3-VL-30B-Instruct | 30B / 3B | 14.5 | 9.0 | 4.5 | 9.3 | 82.0 | 17.6 |
| Qwen3-VL-30B-Thinking | 30B / 3B | 16.5 | 8.8 | 3.8 | 9.7 | 77.8 | 17.5 |
| Qwen3-VL-235B-Instruct | 235B / 22B | 9.6 | 3.0 | 2.6 | 5.1 | **100.0** | 15.9 |
| InternVL3.5-30B-A3B | 30B / 3B | 4.7 | 3.9 | 3.8 | 4.2 | **100.0** | 15.0 |
| _Proprietary models_ | | | | | | | |
| **Gemini 3.1 Pro** | — | **60.5** | **38.9** | **22.7** | **40.7** | 98.4 | **47.2** |
| Gemini 3 Flash | — | 52.5 | 32.5 | 18.2 | 34.4 | 91.4 | 40.9 |
| Claude Opus 4.7 | — | 41.2 | 30.5 | 21.8 | 31.2 | 99.6 | 38.9 |
| GPT-5.4 | — | 48.8 | 30.5 | 12.2 | 30.5 | 99.6 | 38.3 |

Trivial always-no-diff baseline: 11.4% Overall.

<!-- LEADERBOARD END -->

> [!TIP]
> Gemini 3.1 Pro leads at **47.2%**, 5.0 pp ahead of the best open-weight model (Kimi K2.5, 42.2%). Seven of thirteen models fall below 30%. Difficulty is strongly property-dependent — across CSS operators, neither pixel magnitude nor CLIP distance reliably predicts recall.

Submit your model: see [`docs/submission.md`](docs/submission.md).

---

## 🚀 Quick Start

```bash
git clone https://github.com/Tencent/DiffSpot.git
cd DiffSpot
pip install -e ".[api]"

export OPENAI_API_KEY=...   # for both the baseline run and the judge

# 1. Run a baseline VLM (loads the HF dataset, writes predictions JSONL)
python baselines/api/run_openai.py \
    --model gpt-5.4 \
    --output results/gpt-5.4/predictions.jsonl

# 2. Score predictions with the official LLM judge (gpt-oss-120b)
python scripts/evaluate.py \
    --predictions results/gpt-5.4/predictions.jsonl \
    --judge-model gpt-oss-120b \
    --output results/gpt-5.4/scores.json

# 3. Print the official metrics table
python scripts/show_results.py results/gpt-5.4/scores.json
```

> [!TIP]
> To target an OpenAI-compatible endpoint (vLLM, sglang, an internal gateway) for the judge, set `OPENAI_BASE_URL`. Anthropic / Google baselines use `ANTHROPIC_API_KEY` / `GOOGLE_API_KEY`.

---

## 📦 Dataset

```python
from datasets import load_dataset

ds = load_dataset("tencent/DiffSpot", split="test")
ex = ds[0]
ex["image_before"]      # PIL.Image
ex["image_after"]       # PIL.Image
ex["ground_truth_diff"] # natural-language description of the change
```

Each row carries the screenshot pair, the benchmark prompt, the natural-language and structured ground truth (`mutation_dicts_json`), the operator, the difficulty tier, and pixel/bbox metadata. Full field reference: the [dataset card](https://huggingface.co/datasets/tencent/DiffSpot).

---

## 🗂️ Repository Layout

```
DiffSpot/
├── diffspot/              # Core package (data loader, judge, metrics)
│   └── prompts/           # VLM and judge prompt templates (versioned)
├── baselines/             # Reference baseline runners
│   ├── api/               # API-hosted models (OpenAI / Anthropic / Google)
│   └── local/             # Self-hosted models via sglang / vllm
├── scripts/               # End-to-end CLIs (eval, metrics, submission prep)
├── docs/                  # Data card, evaluation protocol, submission guide
├── examples/              # Sample predictions + walkthrough
├── results/               # Per-model raw predictions + scores (reproducibility)
├── leaderboard/           # Machine-readable leaderboard + auto-update tooling
└── space/                 # HuggingFace Space demo source
```

---

## 📚 Citation

```bibtex
@article{diffspot2026,
  title  = {DiffSpot: Can VLMs Spot Fine-Grained Visual Differences in Web Interfaces?},
  author = {TBD},
  year   = {2026},
  note   = {arXiv preprint TBD}
}
```

---

## 🙏 Acknowledgements

DiffSpot builds on prior visual-diff benchmarks ([CLEVR-Change](https://arxiv.org/abs/1901.02527), [Spot-the-Diff](https://arxiv.org/abs/1808.10584), [D³](https://arxiv.org/abs/2410.02651)) and programmatic UI mutation work ([UIClip](https://arxiv.org/abs/2404.12500)). See the paper for the full related-work table.

---

## 📄 License

DiffSpot-Bench (code and dataset) is released under the **MIT License** — see [`LICENSE`](LICENSE). Copyright (C) 2026 Tencent. All rights reserved.
