"""Tests for diffspot.metrics.aggregate()."""

from __future__ import annotations

from diffspot.metrics import aggregate


def _item(id_: str, split: str, operator: str | None, tp: bool, tn: bool) -> dict:
    return {
        "id": id_,
        "split": split,
        "operator": operator,
        "is_true_positive": tp,
        "is_true_negative": tn,
    }


def test_empty():
    r = aggregate([])
    assert r.overall_accuracy == 0.0
    assert r.diff_overall_recall == 0.0
    assert r.no_diff_specificity == 0.0
    assert r.n_total == 0


def test_perfect_score():
    items = [
        _item("e1", "easy", "color", True, False),
        _item("m1", "medium", "color", True, False),
        _item("h1", "hard", "color", True, False),
        _item("n1", "no_diff", None, False, True),
    ]
    r = aggregate(items)
    assert r.overall_accuracy == 1.0
    assert r.diff_overall_recall == 1.0
    assert r.no_diff_specificity == 1.0


def test_worst_score():
    items = [
        _item("e1", "easy", "color", False, False),
        _item("n1", "no_diff", None, False, False),
    ]
    r = aggregate(items)
    assert r.overall_accuracy == 0.0
    assert r.diff_overall_recall == 0.0
    assert r.no_diff_specificity == 0.0


def test_simple_proportions():
    """100 has-diff with 60 TP + 50 no-diff with 40 TN."""
    items = []
    for i in range(60):
        items.append(_item(f"e_tp_{i}", "easy", "color", True, False))
    for i in range(40):
        items.append(_item(f"e_fn_{i}", "easy", "color", False, False))
    for i in range(40):
        items.append(_item(f"n_tn_{i}", "no_diff", None, False, True))
    for i in range(10):
        items.append(_item(f"n_fp_{i}", "no_diff", None, False, False))

    r = aggregate(items)
    assert r.n_total == 150
    assert r.n_has_diff == 100
    assert r.n_no_diff == 50
    assert r.n_tp == 60
    assert r.n_tn == 40
    assert r.diff_overall_recall == 0.6
    assert r.no_diff_specificity == 0.8
    assert r.overall_accuracy == 100 / 150


def test_per_operator_breakdown():
    items = [
        _item("a1", "easy", "color", True, False),
        _item("a2", "easy", "color", False, False),
        _item("b1", "medium", "text", True, False),
        _item("b2", "medium", "text", True, False),
    ]
    r = aggregate(items)
    assert r.by_operator["color"].recall == 0.5
    assert r.by_operator["color"].n_pairs == 2
    assert r.by_operator["text"].recall == 1.0
    assert r.by_operator["text"].n_pairs == 2


def test_gemini_31_pro_matches_paper():
    """Reproduce the Gemini 3.1 Pro main-table row from paper-derived counts.

    Paper main table (row "Gemini 3.1 Pro"):
        Easy 60.5% / Med 38.9% / Hard 22.7% / Diff Overall 40.7% /
        No-Diff 98.4% / Overall 47.2%

    Reverse-engineered exact integer counts (each tier has 1,300 has-diff
    pairs; no-diff tier has 500 pairs):
        Easy TPs = 786   (786 / 1,300 = 60.46% -> 60.5% rounded)
        Med  TPs = 506   (506 / 1,300 = 38.92% -> 38.9%)
        Hard TPs = 295   (295 / 1,300 = 22.69% -> 22.7%)
        No-Diff TNs = 492 (492 / 500   = 98.40%)
    """
    items = []
    counts = {"easy": 786, "medium": 506, "hard": 295}
    for tier, n_tp in counts.items():
        for i in range(n_tp):
            items.append(_item(f"{tier}_tp_{i}", tier, "color", True, False))
        for i in range(1300 - n_tp):
            items.append(_item(f"{tier}_fn_{i}", tier, "color", False, False))
    for i in range(492):
        items.append(_item(f"nd_tn_{i}", "no_diff", None, False, True))
    for i in range(8):
        items.append(_item(f"nd_fp_{i}", "no_diff", None, False, False))

    r = aggregate(items)
    assert r.n_total == 4400
    assert r.n_has_diff == 3900
    assert r.n_no_diff == 500
    assert r.n_tp == 786 + 506 + 295  # 1587
    assert r.n_tn == 492
    assert r.overall_accuracy == (1587 + 492) / 4400  # exactly 47.25%
    assert r.diff_overall_recall == 1587 / 3900
    assert r.no_diff_specificity == 492 / 500
    assert round(r.by_tier["easy"].recall * 100, 1) == 60.5
    assert round(r.by_tier["medium"].recall * 100, 1) == 38.9
    assert round(r.by_tier["hard"].recall * 100, 1) == 22.7
    assert round(r.diff_overall_recall * 100, 1) == 40.7
    assert round(r.no_diff_specificity * 100, 1) == 98.4
    # Paper rounds 47.25% to 47.2; Python's round() can yield 47.2 or 47.3
    # depending on float representation. Allow either.
    assert round(r.overall_accuracy * 100, 1) in (47.2, 47.3)
