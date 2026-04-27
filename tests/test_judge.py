"""Tests for diffspot.judge prompt rendering, JSON parsing, and label reduction.

These tests do NOT call the OpenAI API. End-to-end judge calls are exercised
by ``scripts/evaluate.py`` against real predictions.
"""

from __future__ import annotations

import pytest

from diffspot.judge import (
    JUDGE_VERSION,
    _parse_judge_json,
    load_prompt,
    reduce_judge_label,
    render_prompt,
)


def test_judge_version_pinned():
    assert JUDGE_VERSION == "v2.0"


def test_load_prompt_strips_header():
    body = load_prompt()
    assert ">>> PROMPT BEGINS BELOW THIS LINE >>>" not in body
    assert body.startswith("You are a judge")


def test_render_prompt_replaces_three_vars():
    out = render_prompt(
        gt_mutations=[{"op": "color", "before": "red", "after": "blue"}],
        gt_description="The button became blue.",
        prediction="I see a blue button now.",
    )
    assert "I see a blue button now." in out
    assert "The button became blue." in out
    # The structured GT JSON should appear (operator name as JSON value)
    assert '"op": "color"' in out
    # The prompt's literal output-schema braces must NOT have been format-escaped.
    assert '"mutations":' in out
    assert '"hallucinations":' in out
    assert '"summary":' in out


def test_render_prompt_does_not_double_substitute():
    """If gt_description happens to contain a literal '{gt_json}' string,
    str.replace must not re-substitute it."""
    out = render_prompt(
        gt_mutations=[{"x": 1}],
        gt_description="A {gt_json} marker should survive.",
        prediction="B",
    )
    assert "A {gt_json} marker should survive." in out


def test_parse_judge_json_strips_fences():
    raw = '```json\n{"mutations": [], "hallucinations": [], "summary": {}}\n```'
    parsed = _parse_judge_json(raw)
    assert parsed["mutations"] == []
    assert parsed["hallucinations"] == []


def test_parse_judge_json_handles_prose_wrap():
    raw = (
        "Here is my judgment:\n"
        '{"mutations": [], "hallucinations": [], "summary": {"correct": 0}}\n\n'
        "Done."
    )
    parsed = _parse_judge_json(raw)
    assert parsed["summary"]["correct"] == 0


def test_parse_judge_json_invalid_raises():
    with pytest.raises(ValueError):
        _parse_judge_json("not json at all")


def test_reduce_label_has_diff_correct():
    label = {
        "mutations": [{"verdict": "correct"}, {"verdict": "missed"}],
        "hallucinations": [],
        "summary": {},
    }
    out = reduce_judge_label(label, is_no_diff=False)
    assert out["is_true_positive"] is True
    assert out["is_true_negative"] is False
    assert out["n_correct_mutations"] == 1


def test_reduce_label_has_diff_all_partial_or_missed():
    label = {
        "mutations": [{"verdict": "partial"}, {"verdict": "missed"}],
        "hallucinations": ["fake"],
        "summary": {},
    }
    out = reduce_judge_label(label, is_no_diff=False)
    assert out["is_true_positive"] is False
    assert out["n_correct_mutations"] == 0
    assert out["n_hallucinations"] == 1


def test_reduce_label_no_diff_clean():
    label = {"mutations": [], "hallucinations": [], "summary": {}}
    out = reduce_judge_label(label, is_no_diff=True)
    assert out["is_true_negative"] is True
    assert out["is_true_positive"] is False


def test_reduce_label_no_diff_hallucinated():
    label = {"mutations": [], "hallucinations": ["a", "b"], "summary": {}}
    out = reduce_judge_label(label, is_no_diff=True)
    assert out["is_true_negative"] is False
    assert out["n_hallucinations"] == 2
