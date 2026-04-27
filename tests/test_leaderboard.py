"""Test the leaderboard markdown renderer."""

from __future__ import annotations

from leaderboard.update import render_table


SAMPLE_ENTRIES = [
    {
        "display_name": "Gemini 3.1 Pro",
        "family": "proprietary",
        "params": "—",
        "easy_recall": 60.5,
        "med_recall": 38.9,
        "hard_recall": 22.7,
        "diff_overall_recall": 40.7,
        "no_diff_specificity": 98.4,
        "overall_accuracy": 47.2,
    },
    {
        "display_name": "Kimi K2.5",
        "family": "open-weight",
        "params": "1T / 32B",
        "easy_recall": 54.2,
        "med_recall": 36.4,
        "hard_recall": 18.6,
        "diff_overall_recall": 36.4,
        "no_diff_specificity": 87.2,
        "overall_accuracy": 42.2,
    },
    {
        "display_name": "InternVL3.5-30B-A3B",
        "family": "open-weight",
        "params": "30B / 3B",
        "easy_recall": 4.7,
        "med_recall": 3.9,
        "hard_recall": 3.8,
        "diff_overall_recall": 4.2,
        "no_diff_specificity": 100.0,
        "overall_accuracy": 15.0,
    },
]


def test_renders_two_groups():
    md = render_table(SAMPLE_ENTRIES)
    assert "_Open-weight models_" in md
    assert "_Proprietary models_" in md


def test_bolds_column_max():
    md = render_table(SAMPLE_ENTRIES)
    # Gemini 3.1 Pro has the max in 6 of 6 numeric cols and Overall.
    # Its display_name should be bolded as Overall champion.
    assert "**Gemini 3.1 Pro**" in md
    # No-Diff column max is 100.0 (InternVL3.5)
    assert "**100.0**" in md


def test_open_weight_sorted_by_overall():
    md = render_table(SAMPLE_ENTRIES)
    # Within Open-weight: Kimi (42.2) should appear before InternVL3.5 (15.0)
    kimi_idx = md.find("Kimi K2.5")
    intern_idx = md.find("InternVL3.5-30B-A3B")
    assert 0 < kimi_idx < intern_idx


def test_empty_entries():
    assert "no entries" in render_table([])
