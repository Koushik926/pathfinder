"""The catalog invariants everything else depends on."""

import numpy as np

from app.ml.embeddings import SPACE
from app.ml.graph import topological_order
from app.store import CATALOG


def test_ids_are_unique_and_resolvable():
    assert len(CATALOG.items) == len({i.id for i in CATALOG.items.values()})


def test_every_prerequisite_exists():
    for item in CATALOG.items.values():
        for prereq in item.prereqs:
            assert prereq in CATALOG.items, f"{item.id} -> missing {prereq}"


def test_prerequisite_graph_is_acyclic():
    # topological_order raises on a cycle; ordering the whole catalog proves it.
    order = topological_order(set(CATALOG.items))
    assert len(order) == len(CATALOG.items)

    position = {item_id: i for i, item_id in enumerate(order)}
    for item in CATALOG.items.values():
        for prereq in item.prereqs:
            assert position[prereq] < position[item.id]


def test_no_item_is_its_own_prerequisite():
    for item in CATALOG.items.values():
        assert item.id not in item.prereqs


def test_every_skill_is_taught_by_at_least_two_items():
    counts: dict[str, int] = {}
    for item in CATALOG.items.values():
        for skill_id in item.skills:
            counts[skill_id] = counts.get(skill_id, 0) + 1
    thin = sorted(s for s in CATALOG.skills if counts.get(s, 0) < 2)
    assert not thin, f"skills with fewer than two items: {thin}"


def test_role_skills_all_exist():
    for role in CATALOG.roles.values():
        unknown = set(role.skills) - set(CATALOG.skills)
        assert not unknown, f"{role.id}: {unknown}"


def test_catalog_contains_projects_and_assessments():
    kinds = {k: 0 for k in ("course", "project", "assessment")}
    for item in CATALOG.items.values():
        kinds[item.kind] += 1
    assert kinds["project"] >= 20
    assert kinds["assessment"] >= 15


def test_embedding_matrices_are_finite_and_normalised():
    for matrix in (SPACE.item_vectors, SPACE.skill_vectors, SPACE.role_vectors):
        assert np.isfinite(matrix).all()
        norms = np.linalg.norm(matrix, axis=1)
        assert np.allclose(norms, 1.0, atol=1e-5)
