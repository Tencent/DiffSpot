"""DiffSpot HuggingFace Space — Gradio app.

Runs against the public HF dataset; no local data is shipped with the Space.
"""

from __future__ import annotations


def build_demo():
    raise NotImplementedError(
        "TODO: gradio.Blocks() with: dataset browser (image_a/image_b/GT), "
        "model picker (calls baselines/*), live judge verdict."
    )


if __name__ == "__main__":
    demo = build_demo()
    demo.launch()
