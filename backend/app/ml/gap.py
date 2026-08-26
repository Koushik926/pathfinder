"""Skill-gap analysis: the difference between where a learner is and where
their goal requires them to be.

The target vector comes from two sources, merged:

  role skills   the career profile the goal resolved to, weighted by how
                central each skill is to that job
  goal skills   skills the learner named directly ("I want to learn RAG"),
                which are trusted at least as much as the role target

The gap for a skill is ``(target - mastery)`` clipped at zero and scaled by
the target's importance, so a large shortfall in a peripheral skill never
outranks a moderate shortfall in a core one. This weighted gap vector is what
the recommender optimises coverage against.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.ml.profiler import LearnerProfile
from app.store import CATALOG, Catalog

# A skill is "met" once mastery reaches this fraction of its target.
MET_RATIO = 0.9
# Floor on goal-named skill importance, so an explicit ask is never trivial.
GOAL_SKILL_FLOOR = 0.55


@dataclass
class SkillGap:
    skill_id: str
    name: str
    category: str
    target: float        # required mastery, 0..1
    mastery: float       # current mastery, 0..1
    gap: float           # raw shortfall, target - mastery, clipped at 0
    weighted_gap: float  # gap * target importance — the ranking quantity
    confidence: float    # how well-evidenced the mastery estimate is

    @property
    def is_met(self) -> bool:
        return self.mastery >= self.target * MET_RATIO


def build_target(
    profile: LearnerProfile, catalog: Catalog = CATALOG
) -> dict[str, float]:
    """The skill vector the learner's goal requires."""
    target: dict[str, float] = {}

    if profile.role_id and profile.role_id in catalog.roles:
        target.update(catalog.roles[profile.role_id].skills)

    # Explicitly named skills override the role target when they ask for more.
    for skill_id, weight in profile.goal_skills.items():
        if skill_id not in catalog.skills:
            continue
        asked = max(GOAL_SKILL_FLOOR, min(1.0, weight))
        target[skill_id] = max(target.get(skill_id, 0.0), asked)

    return target


def analyse_gaps(
    profile: LearnerProfile,
    mastery: dict[str, float],
    confidence: dict[str, float] | None = None,
    catalog: Catalog = CATALOG,
    include_met: bool = False,
) -> list[SkillGap]:
    """Rank the learner's skill gaps, largest weighted gap first."""
    confidence = confidence or {}
    target = build_target(profile, catalog)

    gaps: list[SkillGap] = []
    for skill_id, required in target.items():
        skill = catalog.skills.get(skill_id)
        if skill is None:
            continue
        current = mastery.get(skill_id, 0.0)
        shortfall = max(0.0, required - current)
        gap = SkillGap(
            skill_id=skill_id,
            name=skill.name,
            category=skill.category,
            target=round(required, 4),
            mastery=round(current, 4),
            gap=round(shortfall, 4),
            weighted_gap=round(shortfall * required, 4),
            confidence=round(confidence.get(skill_id, 0.0), 4),
        )
        if include_met or not gap.is_met:
            gaps.append(gap)

    gaps.sort(key=lambda g: (-g.weighted_gap, g.skill_id))
    return gaps


def gap_vector(gaps: list[SkillGap]) -> dict[str, float]:
    """Weighted gaps as a plain dict, for the recommender's coverage scoring."""
    return {g.skill_id: g.weighted_gap for g in gaps if g.weighted_gap > 0}


def readiness(
    profile: LearnerProfile, mastery: dict[str, float], catalog: Catalog = CATALOG
) -> float:
    """Overall progress toward the goal, in [0, 1].

    Importance-weighted: mastering the skills that matter most to the role
    moves this further than mastering peripheral ones.
    """
    target = build_target(profile, catalog)
    if not target:
        return 0.0
    total = sum(target.values())
    achieved = sum(
        min(mastery.get(skill_id, 0.0), required) for skill_id, required in target.items()
    )
    return round(achieved / total, 4) if total else 0.0
