"""The evaluation harness is a claim about quality, so it gets tested too.

These are not tests of the numbers — numbers move when the catalog or the
weights move, and pinning them would make every improvement look like a
regression. They test the *properties* the numbers are supposed to have, and
the honesty of the instrument that produces them.
"""

from __future__ import annotations

import pytest

from app.ml.evaluate import (
    STRATEGIES,
    build_cohort,
    run,
    score_path,
)
from app.ml.graph import missing_prerequisites
from app.store import CATALOG

BASELINES = ["popularity", "semantic", "coverage_only"]


@pytest.fixture(scope="module")
def result():
    return run(size=24)


def test_synthetic_histories_are_prerequisite_closed():
    """A learner who finished an item must have finished its prerequisites.

    If the cohort contained impossible histories, every graph-aware strategy
    would score well for a reason that has nothing to do with being good.
    """
    for learner in build_cohort(24):
        completed = set(learner.completed)
        for item_id in completed:
            assert not missing_prerequisites(item_id, completed - {item_id}, CATALOG), (
                f"{learner.id} completed {item_id} without its prerequisites"
            )


def test_cohort_covers_every_role_and_includes_cold_starts():
    cohort = build_cohort(len(CATALOG.roles) * 2)
    assert {l.role_id for l in cohort} == set(CATALOG.roles)
    assert any(not l.completed for l in cohort), "no cold-start learners in the cohort"


def test_paths_are_followable_in_the_order_given(result):
    """The headline claim: every PathFinder item is reachable when it arrives."""
    assert result["strategies"]["pathfinder"]["prerequisite_validity"] == 1.0


def test_pathfinder_beats_every_baseline_on_achievable_gain(result):
    ours = result["strategies"]["pathfinder"]["achievable_gain"]
    for name in BASELINES:
        assert ours > result["strategies"][name]["achievable_gain"], (
            f"{name} matched or beat PathFinder on achievable gain"
        )


def test_pathfinder_is_more_efficient_per_hour(result):
    """Learners spend hours, not items. Gain per 100 hours is the real test."""
    ours = result["strategies"]["pathfinder"]["gain_per_100h"]
    for name in BASELINES:
        assert ours > result["strategies"][name]["gain_per_100h"]


def test_no_item_is_chosen_that_teaches_nothing_needed(result):
    """Regression guard: `_ensure_projects` once padded paths with off-goal work.

    Scaffolding is exempt by definition — it is pulled in to unlock something,
    not because it covers a gap.
    """
    assert result["strategies"]["pathfinder"]["redundancy"] == 0.0


def test_baselines_promise_more_than_they_deliver(result):
    """The comparison is only meaningful if the instrument catches this.

    A strategy that ignores prerequisites looks strong when you assume the
    learner completes everything, and collapses when you count only what they
    could actually reach. PathFinder should lose nothing between the two.
    """
    ours = result["strategies"]["pathfinder"]
    assert ours["achievable_gain"] == pytest.approx(ours["readiness_gain"], abs=1e-9)

    ablation = result["strategies"]["coverage_only"]
    assert ablation["achievable_gain"] < 0.6 * ablation["readiness_gain"]


def test_scoring_is_blind_to_which_strategy_produced_the_path():
    """One instrument, applied identically, or the comparison proves nothing."""
    learner = build_cohort(4)[1]
    items = STRATEGIES["popularity"](learner, 200, CATALOG, None)
    assert score_path(learner, items, CATALOG) == score_path(learner, items, CATALOG)


def test_evaluation_is_reproducible():
    assert run(size=8, seed=7) == run(size=8, seed=7)


def test_a_path_is_not_a_reading_list(result):
    """Job-readiness needs building, not only watching."""
    assert result["strategies"]["pathfinder"]["applied_rate"] >= 0.9
