"""DiffSpot HuggingFace Space — interactive benchmark browser.

Shows random items from the public HF dataset side-by-side with the GT
mutation record. Optional model run + judge verdict is left as an exercise
once the dataset is published; until then this file boots a lightweight
viewer.
"""

from __future__ import annotations

import random

try:
    import gradio as gr
except ImportError:
    raise SystemExit("gradio is required: pip install gradio>=4.40.0")

from diffspot.data import HF_DATASET_ID, load


SPLITS = ["easy", "medium", "hard", "no_diff"]


def _try_load_split(split: str):
    try:
        return list(load(split=split))
    except Exception as e:
        return e


def _sample(split: str):
    items = _try_load_split(split)
    if isinstance(items, Exception):
        return None, None, f"Could not load dataset: {items}", None
    if not items:
        return None, None, f"Split '{split}' is empty.", None
    it = random.choice(items)
    return (
        it.image_a,
        it.image_b,
        it.gt_description or "(no description)",
        it.gt_mutations,
    )


def build_demo() -> "gr.Blocks":
    with gr.Blocks(title="DiffSpot Browser") as demo:
        gr.Markdown("# DiffSpot — Visual Diff Detection Benchmark")
        gr.Markdown(
            f"Dataset: `{HF_DATASET_ID}`\n\n"
            "Pick a split, click **Sample random item**, and inspect the screenshot "
            "pair alongside the structured ground-truth mutation record."
        )

        with gr.Row():
            split_dropdown = gr.Dropdown(SPLITS, value="easy", label="Split")
            sample_btn = gr.Button("Sample random item", variant="primary")

        with gr.Row():
            img_a = gr.Image(label="Image A (original)", type="pil")
            img_b = gr.Image(label="Image B (mutated)", type="pil")

        with gr.Row():
            gt_box = gr.Textbox(label="Ground-truth description", lines=3)
            mut_box = gr.JSON(label="Structured mutation record")

        sample_btn.click(
            _sample,
            inputs=[split_dropdown],
            outputs=[img_a, img_b, gt_box, mut_box],
        )

        gr.Markdown(
            "_To run a model live and see the judge verdict, install the "
            "[`diffspot`](https://github.com/) package and use "
            "`baselines/api/run_openai.py` from the GitHub repo._"
        )
    return demo


if __name__ == "__main__":
    build_demo().launch()
