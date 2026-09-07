"""Turning recommendation arithmetic into an explanation a learner believes.

The important property here is that explanations are *derived from the score*,
not written alongside it. Every sentence traces to a number the ranker actually
used: the component contributions, the skills the item covers, the prerequisite
state. A system that ranks with one model and explains with another can produce
confident, fluent, wrong justifications — so we read the attributions instead.

When an Anthropic API key is present, ``app.llm`` rewrites these facts into
warmer prose. It is given the facts and told not to invent others, so the
explanation stays faithful whether or not the key exists.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.ml.profiler import LearnerProfile
from app.ml.recommender import WEIGHTS, ScoredItem
from app.store import CATALOG, Catalog

COMPONENT_PHRASES = {
    "coverage": "it closes the skill gaps that matter most for your goal",
    "semantic": "it lines up closely with how you described your goal",
    "collab": "learners with a history like yours took this next",
    "level_fit": "it sits at the right difficulty for where you are now",
    "quality": "it is exceptionally well rated by people who took it",
    "modality": "it is in the learning format you prefer",
}


# Components that only mean something when the learner actually supplied the
# evidence behind them. `modality` scores 1.0 for every item when no format
# preference was stated, and `collab` is 0 for a learner with no history — in
# both cases the number is real but says nothing about *this* learner, and a
# sentence like "it is in the learning format you prefer" would be a claim of
# personalisation that did not happen.
CONDITIONAL_COMPONENTS = {"modality": "preferred_modalities", "collab": "completed"}


def _informative_components(profile: LearnerProfile | None) -> set[str]:
    """Which component phrases we are entitled to say out loud."""
    live = set(WEIGHTS)
    if profile is None:
        return live
    for component, field_name in CONDITIONAL_COMPONENTS.items():
        if not getattr(profile, field_name, None):
            live.discard(component)
    return live


@dataclass
class Explanation:
    item_id: str
    headline: str
    reasons: list[str]
    covers: list[dict]
    prerequisites: list[dict]
    unlocks: list[str]
    evidence: dict[str, float]
    # Items in this learner's path that depend on this one, from the graph.
    required_for: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.required_for is None:
            self.required_for = []

    def as_text(self) -> str:
        lines = [self.headline, *(f"- {r}" for r in self.reasons)]
        return "\n".join(lines)


def _join(names: list[str]) -> str:
    """Join names into readable English: "a", "a and b", "a, b and c"."""
    if len(names) <= 1:
        return names[0] if names else ""
    return ", ".join(names[:-1]) + f" and {names[-1]}"


def _describe_skills(covers: dict[str, float], catalog: Catalog, limit: int = 3) -> list[str]:
    ranked = sorted(covers.items(), key=lambda kv: -kv[1])[:limit]
    return [catalog.skill_name(skill_id) for skill_id, _ in ranked]


def explain_item(
    scored: ScoredItem,
    catalog: Catalog = CATALOG,
    mastery: dict[str, float] | None = None,
    position: int | None = None,
    required_for: list[str] | None = None,
    profile: LearnerProfile | None = None,
) -> Explanation:
    """Build a faithful explanation for one recommended item.

    ``required_for`` names the items *in this learner's path* that depend on
    this one. It is read from the prerequisite graph, never inferred. An item
    pulled in purely as groundwork closes no gap of its own, and without this
    it fell through to "consolidates what you have already started" — which is
    plainly false for a learner with no history, and tells them nothing about
    why a linear algebra course appeared in a data science path.
    """
    mastery = mastery or {}
    required_for = required_for or []
    informative = _informative_components(profile)
    item = catalog.items[scored.item_id]

    covered = _describe_skills(scored.covers, catalog)
    if covered:
        headline = f"{item.title} — because you still need {_join(covered)}."
    elif required_for:
        headline = f"{item.title} — required before {_join(required_for)}."
    else:
        headline = f"{item.title} — it consolidates what you have already started."

    reasons: list[str] = []

    # Groundwork earns its place from the graph, not from the ranker, so say so
    # first — it is the whole answer to "why is this here?".
    if required_for:
        reasons.append(
            f"{_join(required_for)} {'depend' if len(required_for) > 1 else 'depends'} "
            f"on this, so it comes first."
        )
        if not covered:
            taught = [catalog.skill_name(s) for s in sorted(item.skills, key=lambda k: -item.skills[k])[:3]]
            reasons.append(
                f"It is not on your goal's skill list itself — it teaches "
                f"{_join(taught)}, which the items above build on."
            )

    # Lead with the component that actually drove the ranking.
    ordered = sorted(scored.contributions.items(), key=lambda kv: -kv[1])
    for name, contribution in ordered[:3]:
        share = contribution / scored.score if scored.score else 0.0
        if share < 0.10:
            continue
        if name not in informative:
            # The number is real; the claim about the learner would not be.
            continue
        phrase = COMPONENT_PHRASES.get(name)
        if phrase:
            reasons.append(f"{phrase.capitalize()} ({share:.0%} of the match score).")

    # Concrete gap arithmetic beats an abstract claim.
    for skill_id, contribution in sorted(scored.covers.items(), key=lambda kv: -kv[1])[:2]:
        current = mastery.get(skill_id, 0.0)
        weight = item.skills.get(skill_id, 0.0)
        reasons.append(
            f"Teaches {catalog.skill_name(skill_id)} at depth {weight:.0%}; "
            f"you are currently at {current:.0%}."
        )

    if scored.missing_prereqs:
        names = [catalog.items[p].title for p in scored.missing_prereqs]
        reasons.append("Scheduled after " + " and ".join(names) + ", which it builds on.")
    elif item.prereqs:
        reasons.append("You have already completed everything this builds on.")

    unlocks = [
        catalog.items[dependent].title
        for dependent in catalog.dependents.get(item.id, [])[:3]
    ]
    if unlocks:
        reasons.append("Opens up: " + ", ".join(unlocks) + ".")

    if position is not None and position == 0:
        reasons.append("This is the highest-value next step in your current path.")

    return Explanation(
        item_id=item.id,
        headline=headline,
        reasons=reasons,
        covers=[
            {
                "skill_id": skill_id,
                "name": catalog.skill_name(skill_id),
                "taught_at": round(item.skills.get(skill_id, 0.0), 3),
                "your_mastery": round(mastery.get(skill_id, 0.0), 3),
                "gap_closed": round(value, 4),
            }
            for skill_id, value in sorted(scored.covers.items(), key=lambda kv: -kv[1])[:5]
        ],
        prerequisites=[
            {"item_id": p, "title": catalog.items[p].title, "met": p not in scored.missing_prereqs}
            for p in item.prereqs
        ],
        unlocks=unlocks,
        required_for=required_for,
        evidence={
            "score": scored.score,
            "weights": WEIGHTS,
            **{f"component_{k}": v for k, v in scored.components.items()},
        },
    )


def explain_path(path, catalog: Catalog = CATALOG) -> dict:
    """A plain-language summary of why the path is shaped the way it is."""
    kinds = {"course": 0, "project": 0, "assessment": 0}
    for item in path.all_items:
        kinds[item.kind] = kinds.get(item.kind, 0) + 1

    top_gaps = [g["name"] for g in path.gap_summary[:3]]
    
    fillers = [i.title for i in path.all_items if i.is_prerequisite_fill]

    strategy = [
        f"Your goal resolved to {path.role_title or 'a custom skill set'}, which needs "
        f"{path.gap_count} skills you have not yet covered.",
        f"The biggest gaps are {_join(top_gaps)}, so the earliest milestones target those.",
        f"The path is {len(path.all_items)} items — {kinds['course']} courses, "
        f"{kinds['project']} projects and {kinds['assessment']} assessments — "
        f"about {path.total_hours} hours, or {path.total_weeks} weeks at your pace.",
        f"Following it should take you from {path.readiness_before:.0%} to "
        f"{path.readiness_after:.0%} readiness against that goal.",
    ]
    if fillers:
        strategy.append(
            "Added as prerequisites you were missing: " + ", ".join(fillers[:4]) + "."
        )
    return {
        "strategy": strategy,
        "coverage": path.coverage,
        "kinds": kinds,
    }
