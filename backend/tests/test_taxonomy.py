"""The ESCO alignment is a credibility claim, so it has to survive scrutiny.

The first two versions of the mapper produced confident nonsense — "Bash &
Shell" aligned to "airport terminal standards", "Reinforcement Learning" to
"insert reinforcement in mould" — because a single shared word was allowed to
count as a match. These tests exist so that class of mistake cannot ship again.
"""

from __future__ import annotations

import json
import pathlib
import sys

import pytest

from app import taxonomy
from app.store import CATALOG

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "scripts"))
import map_esco  # noqa: E402


def test_every_aligned_skill_exists_in_the_catalog():
    for skill_id in taxonomy.MAPPING:
        assert skill_id in CATALOG.skills, f"alignment references unknown skill {skill_id}"


def test_unmapped_skills_are_real_and_disjoint_from_mapped():
    for skill_id in taxonomy.UNMAPPED:
        assert skill_id in CATALOG.skills
        assert skill_id not in taxonomy.MAPPING


def test_every_skill_is_accounted_for():
    """No skill may be silently omitted — it is either aligned or declared not."""
    assert set(taxonomy.MAPPING) | set(taxonomy.UNMAPPED) == set(CATALOG.skills)


def test_alignments_point_at_real_esco_uris():
    for skill_id, concept in taxonomy.MAPPING.items():
        assert concept["uri"].startswith("http://data.europa.eu/esco/"), skill_id
        assert concept["esco_label"], skill_id


def test_no_alignment_is_kept_below_the_threshold():
    for skill_id, concept in taxonomy.MAPPING.items():
        assert concept["similarity"] >= map_esco.ACCEPT, skill_id


def test_summary_reports_its_own_gaps():
    summary = taxonomy.summary(len(CATALOG.skills))
    assert summary["aligned"] + len(summary["no_esco_concept"]) == len(CATALOG.skills)
    assert 0.0 <= summary["coverage"] <= 1.0


def test_a_missing_mapping_file_does_not_break_the_service():
    """The alignment is an annotation. Its absence is not an outage."""
    original = taxonomy._PATH
    try:
        taxonomy._PATH = pathlib.Path("/nonexistent/skills_esco.json")
        assert taxonomy._load()["mapping"] == {}
    finally:
        taxonomy._PATH = original


@pytest.mark.parametrize(
    "ours,theirs",
    [
        ("Bash & Shell", "airport terminal standards"),
        ("Authentication & Security", "prepare exercise session"),
        ("Reinforcement Learning", "insert reinforcement in mould"),
        ("Computer Vision", "computer programming"),
        ("Cloud Security", "Parrot Security OS"),
        ("Android Development", "engage composers"),
        ("Technical Writing", "manage manufacturing documentation"),
        ("Interview Preparation", "outplacement"),
    ],
)
def test_a_shared_word_is_not_a_match(ours, theirs):
    """Every one of these was a confident alignment in an earlier run."""
    assert map_esco.similarity(ours, theirs) < map_esco.ACCEPT


@pytest.mark.parametrize(
    "ours,theirs",
    [
        ("Robotics", "robotics"),
        ("Natural Language Processing", "natural language processing"),
        ("Machine Learning", "machine learning algorithms"),
        ("Functional Programming", "use functional programming"),
        ("Cyber Security", "cyber security"),
    ],
)
def test_real_matches_still_pass(ours, theirs):
    """Strictness that rejects everything would be worthless."""
    assert map_esco.similarity(ours, theirs) >= map_esco.ACCEPT


def test_the_mapping_file_is_valid_json_with_the_fields_we_publish():
    document = json.loads(taxonomy._PATH.read_text())
    for field in ("taxonomy", "source", "accept_threshold", "mapping", "unmapped"):
        assert field in document
