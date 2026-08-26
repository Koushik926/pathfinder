"""Learner profiling: turn a learning history into a skill mastery vector.

The core modelling choice is that mastery *saturates* rather than sums. Two
courses that each teach Python at weight 0.5 should not produce mastery 1.0 —
they overlap. Treating each completion as independent evidence and combining
with a noisy-OR

    mastery = 1 - prod(1 - contribution_i)

gives diminishing returns: the first course on a topic moves the needle a lot,
the fourth barely at all. That matches how the gap engine should behave — it
should stop recommending Python once the learner plainly knows Python.

Each contribution is discounted by three factors:

  depth    an advanced item teaches a skill more thoroughly than a beginner one
  recency  skills fade; a course finished three years ago counts for less
  score    an assessment result, when we have one, is direct evidence
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from app.store import CATALOG, Catalog

# Months after which a completion's contribution halves.
RECENCY_HALFLIFE_MONTHS = 24.0
# Recency never decays past this: you don't forget everything.
RECENCY_FLOOR = 0.35
# Assumed mastery evidence for a completed item with no assessment score.
DEFAULT_COMPLETION_SCORE = 0.85
# Per-item contribution ceiling, so no single course claims full mastery.
MAX_SINGLE_CONTRIBUTION = 0.92

LEVEL_DEPTH_FACTOR = {1: 0.85, 2: 1.0, 3: 1.15}

# How much a learner's self-declared level is trusted relative to hard evidence.
DECLARED_WEIGHT = 0.7


@dataclass
class Completion:
    """One finished catalog item in a learner's history."""

    item_id: str
    months_ago: float = 6.0
    score: float | None = None      # 0..1, from an assessment or self-report

    def evidence(self) -> float:
        return DEFAULT_COMPLETION_SCORE if self.score is None else max(0.0, min(1.0, self.score))


@dataclass
class LearnerProfile:
    """Everything PathFinder knows about one learner."""

    id: str
    name: str = "Learner"
    goal_text: str = ""
    role_id: str | None = None
    experience_level: int = 1               # 1 beginner, 2 intermediate, 3 advanced
    hours_per_week: float = 8.0
    preferred_modalities: list[str] = field(default_factory=list)
    interests: list[str] = field(default_factory=list)
    completed: list[Completion] = field(default_factory=list)
    declared_skills: dict[str, float] = field(default_factory=dict)   # skill -> 0..1
    # Skills the learner explicitly asked for, beyond the role target.
    goal_skills: dict[str, float] = field(default_factory=dict)

    @property
    def completed_ids(self) -> set[str]:
        return {c.item_id for c in self.completed}


def recency_factor(months_ago: float) -> float:
    """Exponential forgetting curve with a floor."""
    decayed = 0.5 ** (max(0.0, months_ago) / RECENCY_HALFLIFE_MONTHS)
    return RECENCY_FLOOR + (1.0 - RECENCY_FLOOR) * decayed


def compute_mastery(
    profile: LearnerProfile, catalog: Catalog = CATALOG
) -> tuple[dict[str, float], dict[str, float]]:
    """Return (mastery, confidence) vectors over skill ids.

    ``mastery`` is the learner's estimated command of each skill in [0, 1].
    ``confidence`` is how much evidence backs that estimate — a skill known
    only from a self-declaration is held with less confidence than one backed
    by three completed courses and an assessment. The explanation layer uses
    it to hedge its language honestly.
    """
    complements: dict[str, float] = {}
    evidence_count: dict[str, float] = {}

    for completion in profile.completed:
        item = catalog.items.get(completion.item_id)
        if item is None:
            continue  # history may reference items outside this catalog
        depth = LEVEL_DEPTH_FACTOR.get(item.level, 1.0)
        recency = recency_factor(completion.months_ago)
        score = completion.evidence()
        # Building or being tested on something is stronger evidence than watching it.
        kind_factor = 1.1 if item.kind in ("assessment", "project") else 1.0

        for skill_id, weight in item.skills.items():
            contribution = min(
                MAX_SINGLE_CONTRIBUTION, weight * depth * recency * score * kind_factor
            )
            complements[skill_id] = complements.get(skill_id, 1.0) * (1.0 - contribution)
            evidence_count[skill_id] = evidence_count.get(skill_id, 0.0) + weight * recency

    mastery = {skill_id: 1.0 - comp for skill_id, comp in complements.items()}

    # Fold in self-declared levels as one more piece of (weaker) evidence.
    for skill_id, declared in profile.declared_skills.items():
        if skill_id not in catalog.skills:
            continue
        declared = max(0.0, min(1.0, declared)) * DECLARED_WEIGHT
        existing = mastery.get(skill_id, 0.0)
        mastery[skill_id] = 1.0 - (1.0 - existing) * (1.0 - declared)
        evidence_count[skill_id] = evidence_count.get(skill_id, 0.0) + 0.5

    confidence = {
        skill_id: round(1.0 - math.exp(-count), 4)
        for skill_id, count in evidence_count.items()
    }

    return (
        {k: round(v, 4) for k, v in sorted(mastery.items(), key=lambda kv: -kv[1])},
        confidence,
    )


def implied_level(profile: LearnerProfile, mastery: dict[str, float]) -> float:
    """Estimate the learner's overall level in [1, 3] from evidence + self-report.

    Used to keep recommendations at an appropriate difficulty: self-reported
    level anchors the estimate, demonstrated breadth of mastery adjusts it.
    """
    strong = sum(1 for value in mastery.values() if value >= 0.6)
    breadth = min(1.0, strong / 18.0)
    return round(min(3.0, 0.6 * profile.experience_level + 1.6 * breadth + 0.4), 2)
