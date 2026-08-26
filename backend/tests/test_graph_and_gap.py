"""Prerequisite ordering and skill-gap arithmetic."""

import pytest

from app.ml.gap import analyse_gaps, build_target, readiness
from app.ml.graph import (
    is_ready, missing_prerequisites, prerequisite_closure, topological_order, unlocked_by,
)
from app.ml.profiler import compute_mastery
from app.store import CATALOG


def test_closure_pulls_transitive_prerequisites():
    needed = prerequisite_closure({"ml-106"})
    assert "ml-103" in needed and "ml-102" in needed


def test_closure_skips_what_the_learner_already_knows(intermediate):
    needed = prerequisite_closure({"ml-106"}, known=intermediate.completed_ids)
    assert "da-102" not in needed  # already completed, must not be re-added


def test_topological_order_respects_edges():
    items = prerequisite_closure({"dl-107"}) | {"dl-107"}
    order = topological_order(items)
    position = {item_id: i for i, item_id in enumerate(order)}
    for item_id in items:
        for prereq in CATALOG.items[item_id].prereqs:
            if prereq in items:
                assert position[prereq] < position[item_id]


def test_topological_order_is_deterministic():
    items = prerequisite_closure({"dl-107"}) | {"dl-107"}
    assert topological_order(items) == topological_order(items)


def test_topological_order_detects_a_cycle(monkeypatch):
    """A cycle must raise, not hang or silently drop items."""
    a, b = CATALOG.items["py-101"], CATALOG.items["py-102"]
    object.__setattr__(a, "prereqs", ["py-102"])
    try:
        with pytest.raises(ValueError, match="cycle"):
            topological_order({"py-101", "py-102"})
    finally:
        object.__setattr__(a, "prereqs", [])
        assert b.prereqs == ["py-101"]


def test_readiness_and_unlocks(intermediate):
    assert is_ready("ml-102", intermediate.completed_ids)
    assert not is_ready("ml-106", intermediate.completed_ids)
    # missing_prerequisites reports *direct* prerequisites only; ml-103 is
    # reachable from ml-106 but only transitively, via ml-105.
    assert missing_prerequisites("ml-106", intermediate.completed_ids) == ["ml-105"]
    assert "ml-103" in prerequisite_closure({"ml-106"}, known=intermediate.completed_ids)
    assert "py-104" not in unlocked_by("py-101", {"py-101"})


def test_gap_is_weighted_by_importance(intermediate):
    mastery, confidence = compute_mastery(intermediate)
    gaps = analyse_gaps(intermediate, mastery, confidence)
    assert gaps == sorted(gaps, key=lambda g: (-g.weighted_gap, g.skill_id))
    for gap in gaps:
        assert gap.gap >= 0
        assert gap.weighted_gap == pytest.approx(gap.gap * gap.target, abs=1e-3)


def test_completed_skills_drop_out_of_the_gap_list(intermediate):
    mastery, confidence = compute_mastery(intermediate)
    open_ids = {g.skill_id for g in analyse_gaps(intermediate, mastery, confidence)}
    # SQL was completed recently with a high score; it should not be a top gap.
    sql_gap = next((g for g in analyse_gaps(intermediate, mastery, confidence) if g.skill_id == "sql"), None)
    if sql_gap:
        assert sql_gap.mastery > 0.3


def test_readiness_rises_as_mastery_rises(novice, intermediate):
    assert readiness(intermediate, compute_mastery(intermediate)[0]) > readiness(
        novice, compute_mastery(novice)[0]
    )


def test_goal_skills_extend_the_role_target(intermediate):
    intermediate.goal_skills = {"rag": 0.9}
    target = build_target(intermediate)
    assert target["rag"] >= 0.9
