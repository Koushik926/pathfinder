"""Mastery estimation behaviour."""

from app.ml.profiler import (
    Completion, LearnerProfile, compute_mastery, implied_level, recency_factor,
)


def test_mastery_saturates_below_one():
    """Stacking overlapping courses must not push a skill past 1.0."""
    profile = LearnerProfile(
        id="x",
        completed=[Completion(i, 0) for i in ("py-101", "py-102", "py-103", "py-104")],
    )
    mastery, _ = compute_mastery(profile)
    assert 0.0 < mastery["python-basics"] < 1.0


def test_more_evidence_increases_mastery_with_diminishing_returns():
    one, _ = compute_mastery(LearnerProfile(id="a", completed=[Completion("py-101", 0)]))
    two, _ = compute_mastery(
        LearnerProfile(id="b", completed=[Completion("py-101", 0), Completion("py-102", 0)])
    )
    three, _ = compute_mastery(
        LearnerProfile(id="c", completed=[Completion(i, 0) for i in ("py-101", "py-102", "py-103")])
    )
    first_jump = two["python-basics"] - one["python-basics"]
    second_jump = three["python-basics"] - two["python-basics"]
    assert two["python-basics"] > one["python-basics"]
    assert second_jump < first_jump


def test_recent_learning_counts_for_more_than_old():
    recent, _ = compute_mastery(LearnerProfile(id="r", completed=[Completion("py-101", 0)]))
    old, _ = compute_mastery(LearnerProfile(id="o", completed=[Completion("py-101", 60)]))
    assert recent["python-basics"] > old["python-basics"]


def test_recency_never_decays_to_zero():
    assert recency_factor(1000) >= 0.3
    assert recency_factor(0) == 1.0


def test_assessment_score_modulates_credit():
    high, _ = compute_mastery(LearnerProfile(id="h", completed=[Completion("sql-101", 0, 1.0)]))
    low, _ = compute_mastery(LearnerProfile(id="l", completed=[Completion("sql-101", 0, 0.2)]))
    assert high["sql"] > low["sql"]


def test_unknown_history_items_are_ignored_not_fatal():
    mastery, _ = compute_mastery(
        LearnerProfile(id="u", completed=[Completion("not-a-real-course", 0)])
    )
    assert mastery == {}


def test_implied_level_rises_with_demonstrated_breadth(novice, intermediate):
    assert implied_level(intermediate, compute_mastery(intermediate)[0]) > implied_level(
        novice, compute_mastery(novice)[0]
    )
