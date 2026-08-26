"""Ranking and path-construction behaviour."""

from datetime import date

from app.ml.gap import analyse_gaps, gap_vector
from app.ml.planner import generate_path
from app.ml.profiler import compute_mastery, implied_level
from app.ml.recommender import RECOMMENDER
from app.store import CATALOG


def _rank(profile, k=10):
    mastery, confidence = compute_mastery(profile)
    level = implied_level(profile, mastery)
    gaps = gap_vector(analyse_gaps(profile, mastery, confidence))
    return RECOMMENDER.recommend(profile, gaps, level, k=k)


def test_never_recommends_something_already_completed(intermediate):
    ranked = _rank(intermediate, k=40)
    assert not (intermediate.completed_ids & {r.item_id for r in ranked})


def test_ranking_is_deterministic(intermediate):
    assert [r.item_id for r in _rank(intermediate)] == [r.item_id for r in _rank(intermediate)]


def test_score_equals_sum_of_its_components(intermediate):
    for scored in _rank(intermediate, k=5):
        if scored.is_ready:  # unready items carry an extra prerequisite discount
            assert abs(sum(scored.contributions.values()) - scored.score) < 1e-3


def test_cold_start_still_produces_recommendations(novice):
    """A learner with no history at all must not get an empty list."""
    ranked = _rank(novice)
    assert len(ranked) >= 5
    assert all(r.score > 0 for r in ranked)


def test_recommendations_serve_the_goal(intermediate):
    """Top picks should teach skills the target role actually needs."""
    role_skills = set(CATALOG.roles["data-scientist"].skills)
    for scored in _rank(intermediate, k=5):
        assert set(CATALOG.items[scored.item_id].skills) & role_skills


def test_diversify_reduces_redundancy(intermediate):
    ranked = _rank(intermediate, k=12)
    diverse = RECOMMENDER.diversify(ranked, k=5)
    assert len(diverse) == 5
    assert len({d.item_id for d in diverse}) == 5


def test_cf_matrix_is_symmetric_with_zero_diagonal():
    matrix = RECOMMENDER.cf_matrix
    assert (matrix.diagonal() == 0).all()
    assert abs(matrix - matrix.T).max() < 1e-6


# -- planner ---------------------------------------------------------------

def test_path_orders_prerequisites_before_dependents(intermediate):
    path = generate_path(intermediate, start=date(2026, 9, 1))
    order = [i.item_id for i in path.all_items]
    position = {item_id: i for i, item_id in enumerate(order)}
    for item in path.all_items:
        for prereq in item.prereqs:
            if prereq in position:
                assert position[prereq] < position[item.item_id], (
                    f"{prereq} must precede {item.item_id}"
                )


def test_path_excludes_completed_items(intermediate):
    path = generate_path(intermediate)
    assert not (intermediate.completed_ids & {i.item_id for i in path.all_items})


def test_path_includes_hands_on_work(intermediate):
    """Coverage-per-hour alone yields a reading list; projects are guaranteed."""
    path = generate_path(intermediate)
    assert sum(1 for i in path.all_items if i.kind == "project") >= 2


def test_path_closes_most_of_the_gap_and_raises_readiness(intermediate):
    path = generate_path(intermediate)
    assert path.coverage >= 0.7
    assert path.readiness_after > path.readiness_before


def test_milestones_partition_the_path_exactly(intermediate):
    path = generate_path(intermediate)
    from_milestones = [i.item_id for m in path.milestones for i in m.items]
    assert len(from_milestones) == len(set(from_milestones))
    assert sum(m.hours for m in path.milestones) == path.total_hours
    assert 3 <= len(path.milestones) <= 5


def test_milestone_dates_run_forward(intermediate):
    path = generate_path(intermediate, start=date(2026, 9, 1))
    previous = "2026-09-01"
    for milestone in path.milestones:
        assert milestone.starts_on >= previous
        assert milestone.ends_on > milestone.starts_on
        previous = milestone.ends_on


def test_pace_changes_schedule_but_not_content(intermediate):
    slow = generate_path(intermediate)
    intermediate.hours_per_week = 30
    fast = generate_path(intermediate)
    assert fast.total_weeks < slow.total_weeks
    assert fast.total_hours == slow.total_hours


def test_beginner_gets_an_easier_path_than_an_experienced_learner(novice, intermediate):
    novice_levels = [i.level for i in generate_path(novice).all_items]
    mid_levels = [i.level for i in generate_path(intermediate).all_items]
    assert sum(novice_levels) / len(novice_levels) <= sum(mid_levels) / len(mid_levels)
