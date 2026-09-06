"""The engine must work on a catalog it was never written for.

PathFinder's value proposition to an institution is that the reasoning is
domain-independent: swap the catalog, keep the engine. That is a claim worth
testing rather than asserting, because it is easy to accidentally bake the
software-careers domain into the algorithms — a hardcoded skill id, a category
name, an assumption that "level 1" means an introductory programming course.

This exercises the full pipeline against a clinical medicine catalog that
shares no skill, role, item id or category with the shipped one. If any engine
grows a domain assumption, these tests fail.
"""

from pathlib import Path

import pytest

from app.ml.embeddings import SemanticSpace
from app.ml.gap import analyse_gaps, gap_vector, readiness
from app.ml.graph import topological_order
from app.ml.planner import generate_path
from app.ml.profiler import LearnerProfile, compute_mastery
from app.ml.recommender import Recommender
from app.store import Catalog, Item, Role, Skill
from app.ml import qa

import json

EXAMPLE_DIR = Path(__file__).resolve().parents[2] / "examples" / "medicine" / "data"

pytestmark = pytest.mark.skipif(
    not EXAMPLE_DIR.is_dir(),
    reason="run examples/medicine/build_catalog.py to generate the alternate catalog",
)


@pytest.fixture(scope="module")
def medicine() -> Catalog:
    def read(name):
        return json.loads((EXAMPLE_DIR / name).read_text())

    return Catalog(
        skills={s["id"]: Skill(**s) for s in read("skills.json")},
        items={i["id"]: Item(**i) for i in read("catalog.json")},
        roles={r["id"]: Role(**r) for r in read("roles.json")},
        interactions=read("interactions.json"),
    )


@pytest.fixture(scope="module")
def engine(medicine):
    space = SemanticSpace(medicine)
    return space, Recommender(medicine, space)


@pytest.fixture
def student():
    return LearnerProfile(
        id="med", role_id="emergency-physician",
        goal_text="I want to become an emergency physician",
        experience_level=1, hours_per_week=12,
    )


def test_catalog_shares_nothing_with_the_shipped_one(medicine):
    """Guards the premise: if the domains overlap, the test proves little."""
    from app.store import CATALOG

    assert not set(medicine.items) & set(CATALOG.items)
    assert not set(medicine.skills) & set(CATALOG.skills)
    assert not set(medicine.roles) & set(CATALOG.roles)


def test_goal_resolves_in_an_unseen_domain(medicine, engine):
    space, _ = engine
    role_id, score = space.match_role("I want to become an emergency physician")
    assert role_id == "emergency-physician"
    assert score > 0.3


def test_gap_analysis_works_on_the_new_domain(medicine, student):
    mastery, confidence = compute_mastery(student, medicine)
    gaps = analyse_gaps(student, mastery, confidence, medicine)
    assert gaps
    assert {g.skill_id for g in gaps} <= set(medicine.skills)
    # A learner with no history starts far from the goal.
    assert readiness(student, mastery, medicine) < 0.2


def test_planner_produces_a_coherent_clinical_path(medicine, engine, student):
    _, recommender = engine
    path = generate_path(student, medicine, recommender)

    assert path.all_items
    assert path.readiness_after > path.readiness_before
    assert 3 <= len(path.milestones) <= 5

    # Prerequisite ordering must hold in any domain.
    order = {item.item_id: i for i, item in enumerate(path.all_items)}
    for item in path.all_items:
        for prereq in medicine.items[item.item_id].prereqs:
            if prereq in order:
                assert order[prereq] < order[item.item_id], (
                    f"{prereq} must precede {item.item_id}"
                )

    # The domain-specific sanity check a clinician would apply.
    if "med-101" in order and "med-102" in order:
        assert order["med-101"] < order["med-102"], "anatomy must precede physiology"


def test_hands_on_work_is_guaranteed_in_any_domain(medicine, engine, student):
    """The projects guarantee is about pedagogy, not about software projects —
    here it should surface clinical rotations."""
    _, recommender = engine
    path = generate_path(student, medicine, recommender)
    rotations = [i for i in path.all_items if i.kind == "project"]
    assert rotations, "a path with no practical work is not a path"


def test_question_answering_reads_the_new_graph(medicine, engine, student):
    _, recommender = engine
    path = generate_path(student, medicine, recommender)

    nxt = qa.answer(student, path, "what should I do first?", medicine)
    assert nxt.intent == "answer_next"
    assert any(item.title in nxt.text for item in path.all_items)

    skip = qa.answer(student, path, "can I skip anatomy?", medicine)
    assert skip.intent == "answer_skip"
    # It must name the actual dependent, read from the graph.
    assert "Physiology" in skip.text or "physiology" in skip.text


def test_ranking_stays_deterministic_on_a_foreign_catalog(medicine, engine, student):
    _, recommender = engine
    mastery, confidence = compute_mastery(student, medicine)
    gaps = gap_vector(analyse_gaps(student, mastery, confidence, medicine))
    first = [s.item_id for s in recommender.recommend(student, gaps, 1.0, k=8)]
    second = [s.item_id for s in recommender.recommend(student, gaps, 1.0, k=8)]
    assert first == second


def test_the_new_catalog_is_itself_a_valid_dag(medicine):
    order = topological_order(set(medicine.items), catalog=medicine)
    assert len(order) == len(medicine.items)
