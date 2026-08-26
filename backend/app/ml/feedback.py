"""Adaptation: how the path changes in response to what the learner does.

Three kinds of signal arrive after a path is generated:

  completion  the learner finished an item, optionally with a score
  reaction    "too easy", "too hard", "not interested", "loved this"
  pace        they are running ahead of or behind the schedule

Rather than patching the existing path in place, each signal is folded back
into the *profile* and the path is regenerated. That keeps one source of truth:
the path is always exactly what the current profile implies, so there is no way
for the roadmap and the learner model to drift apart. Regeneration costs
milliseconds, which is what makes this affordable.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.ml.profiler import Completion, LearnerProfile
from app.store import CATALOG, Catalog

# How strongly a reaction shifts the learner's level estimate.
LEVEL_STEP = 0.5
# Mastery credited when a learner says an item was "too easy" — they likely
# already knew the material, so we record it as known without a completion.
TOO_EASY_CREDIT = 0.75


@dataclass
class FeedbackResult:
    profile: LearnerProfile
    changes: list[str]
    regenerate: bool


def apply_completion(
    profile: LearnerProfile, item_id: str, score: float | None = None, catalog: Catalog = CATALOG
) -> FeedbackResult:
    """Record a finished item and let it update the mastery model."""
    if item_id not in catalog.items:
        return FeedbackResult(profile, [f"Unknown item {item_id}."], False)

    if item_id in profile.completed_ids:
        return FeedbackResult(profile, ["Already recorded."], False)

    profile.completed.append(Completion(item_id=item_id, months_ago=0.0, score=score))
    item = catalog.items[item_id]
    changes = [f"Marked '{item.title}' complete."]
    if score is not None:
        changes.append(f"Recorded a score of {score:.0%}, which sharpens the mastery estimate.")
        if score < 0.6:
            changes.append(
                "A low score means the skills are credited only partially, so "
                "reinforcement may reappear in your path."
            )
    return FeedbackResult(profile, changes, regenerate=True)


def apply_reaction(
    profile: LearnerProfile, item_id: str, reaction: str, catalog: Catalog = CATALOG
) -> FeedbackResult:
    """Fold a learner's reaction to an item back into their profile."""
    item = catalog.items.get(item_id)
    if item is None:
        return FeedbackResult(profile, [f"Unknown item {item_id}."], False)

    changes: list[str] = []
    reaction = reaction.lower().replace(" ", "_")

    if reaction == "too_easy":
        # They already know this. Credit the skills and raise the difficulty target.
        for skill_id, weight in item.skills.items():
            current = profile.declared_skills.get(skill_id, 0.0)
            profile.declared_skills[skill_id] = max(current, weight * TOO_EASY_CREDIT)
        profile.experience_level = min(3, profile.experience_level + 1)
        changes.append(
            f"Credited the skills '{item.title}' teaches and raised your level, "
            "so later recommendations start harder."
        )

    elif reaction == "too_hard":
        profile.experience_level = max(1, profile.experience_level - 1)
        changes.append(
            f"Lowered the difficulty target and will insert groundwork before "
            f"'{item.title}' rather than dropping it."
        )

    elif reaction == "not_interested":
        # Suppress the topic by zeroing it out of the goal, not the catalog.
        for skill_id in item.skills:
            if skill_id in profile.goal_skills:
                del profile.goal_skills[skill_id]
        changes.append(
            f"Removed '{item.title}' and de-emphasised its topic in your goal. "
            "Skills your target role still requires will remain."
        )

    elif reaction in ("loved", "more_like_this"):
        for skill_id, weight in item.skills.items():
            profile.goal_skills[skill_id] = max(profile.goal_skills.get(skill_id, 0.0), weight)
        changes.append(f"Weighted your goal toward more work like '{item.title}'.")

    else:
        return FeedbackResult(profile, [f"Unrecognised reaction '{reaction}'."], False)

    return FeedbackResult(profile, changes, regenerate=True)


def apply_pace(profile: LearnerProfile, hours_per_week: float) -> FeedbackResult:
    """Update the weekly budget, which rescales the whole schedule."""
    hours_per_week = max(1.0, min(60.0, hours_per_week))
    previous = profile.hours_per_week
    profile.hours_per_week = hours_per_week
    return FeedbackResult(
        profile,
        [f"Pace changed from {previous:g} to {hours_per_week:g} hours per week; "
         "milestone dates have been rescheduled."],
        regenerate=True,
    )
