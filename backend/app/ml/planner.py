"""Learning path generation.

Selecting a path is a budgeted maximum-coverage problem: choose a set of items
that covers as much of the learner's weighted skill gap as possible, subject to
a time budget, while respecting prerequisites.

That objective is submodular — the second course on a topic adds less than the
first — so the greedy algorithm (repeatedly take the item with the best
marginal gain per hour) carries the standard (1 - 1/e) approximation guarantee
and runs in milliseconds. After each pick we simulate the mastery the learner
would gain, using the same noisy-OR rule the profiler uses, and recompute the
remaining gap. That simulation is what stops the planner from stacking four
overlapping intro-to-ML courses: once the first is taken, the others' marginal
value collapses.

The selected set is then closed under prerequisites, topologically ordered, and
chunked into milestones with a schedule derived from the learner's weekly hours.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, timedelta

from app.ml.gap import analyse_gaps, gap_vector, readiness
from app.ml.graph import prerequisite_closure, topological_order
from app.ml.profiler import LearnerProfile, compute_mastery, implied_level
from app.ml.recommender import RECOMMENDER, Recommender, ScoredItem
from app.store import CATALOG, Catalog

# Stop once this fraction of the initial weighted gap is covered.
COVERAGE_TARGET = 0.82
# Hard ceiling on path length, so a path stays something a human can face.
MAX_SELECTED = 22
# Efficiency exponent on hours: 0 ignores cost, 1 is strict gain-per-hour.
# A square root favours substantial courses over a pile of tiny ones.
COST_EXPONENT = 0.5
# Target number of milestones.
MIN_PHASES, MAX_PHASES = 3, 5
# Projects and assessments consolidate and verify skills rather than introduce
# them, so raw gap-coverage-per-hour systematically undervalues them. These
# multipliers correct for that in the greedy selection.
KIND_BONUS = {"course": 1.0, "project": 1.3, "assessment": 1.15}
# A path with no build-something-real work is not a usable path, whatever the
# coverage arithmetic says. Guaranteed after greedy selection.
MIN_PROJECTS = 2


@dataclass
class PathItem:
    item_id: str
    title: str
    kind: str
    provider: str
    hours: int
    level: int
    modality: str
    skills: dict[str, float]
    prereqs: list[str]
    rating: float
    url_hint: str = ""
    reason_components: dict[str, float] = field(default_factory=dict)
    covers: dict[str, float] = field(default_factory=dict)
    is_prerequisite_fill: bool = False


@dataclass
class Milestone:
    index: int
    title: str
    focus_skills: list[str]
    items: list[PathItem]
    hours: int
    weeks: float
    starts_on: str
    ends_on: str

    @property
    def item_ids(self) -> list[str]:
        return [i.item_id for i in self.items]


@dataclass
class LearningPath:
    profile_id: str
    goal_text: str
    role_id: str | None
    role_title: str | None
    milestones: list[Milestone]
    total_hours: int
    total_weeks: float
    coverage: float          # fraction of initial weighted gap closed
    gap_count: int           # total unmet skills, before gap_summary truncation
    readiness_before: float
    readiness_after: float
    gap_summary: list[dict]
    generated_on: str

    @property
    def all_items(self) -> list[PathItem]:
        return [item for milestone in self.milestones for item in milestone.items]


def _simulate_gain(mastery: dict[str, float], item_skills: dict[str, float], level: int) -> None:
    """Apply the mastery a learner would gain from completing an item, in place.

    Mirrors ``profiler.compute_mastery``: noisy-OR combination, discounted by
    item depth. Recency is 1.0 because the item is being taken now.
    """
    depth = {1: 0.85, 2: 1.0, 3: 1.15}.get(level, 1.0)
    for skill_id, weight in item_skills.items():
        contribution = min(0.92, weight * depth * 0.85)
        current = mastery.get(skill_id, 0.0)
        mastery[skill_id] = 1.0 - (1.0 - current) * (1.0 - contribution)


def _phase_title(catalog: Catalog, items: list[PathItem], index: int, total: int) -> str:
    """Name a milestone after the skill category it is mostly about."""
    weight_by_category: dict[str, float] = {}
    for item in items:
        for skill_id, weight in item.skills.items():
            skill = catalog.skills.get(skill_id)
            if skill:
                weight_by_category[skill.category] = weight_by_category.get(skill.category, 0.0) + weight
    category = max(weight_by_category, key=weight_by_category.get) if weight_by_category else "Core"

    if index == 0:
        prefix = "Foundations"
    elif index == total - 1:
        prefix = "Mastery"
    else:
        prefix = "Building"
    return f"{prefix}: {category}"


def _chunk_into_milestones(
    ordered: list[PathItem], hours_per_week: float, catalog: Catalog, start: date
) -> list[Milestone]:
    """Split the ordered path into roughly equal-effort phases.

    Splitting on cumulative hours (rather than item count) keeps milestones
    comparable in duration, which is what makes a progress bar meaningful.
    """
    if not ordered:
        return []

    total_hours = sum(item.hours for item in ordered)
    n_phases = max(MIN_PHASES, min(MAX_PHASES, round(total_hours / 45) or MIN_PHASES))
    n_phases = min(n_phases, len(ordered))
    target = total_hours / n_phases

    buckets: list[list[PathItem]] = [[] for _ in range(n_phases)]
    running = 0.0
    phase = 0
    for item in ordered:
        buckets[phase].append(item)
        running += item.hours
        # Advance when this phase is full, keeping room for remaining phases.
        remaining_phases = n_phases - phase - 1
        if remaining_phases > 0 and running >= target * (phase + 1):
            if len(ordered) - (sum(len(b) for b in buckets)) >= remaining_phases:
                phase += 1

    buckets = [b for b in buckets if b]

    milestones: list[Milestone] = []
    cursor = start
    for index, bucket in enumerate(buckets):
        hours = sum(item.hours for item in bucket)
        weeks = round(hours / max(1.0, hours_per_week), 1)
        ends = cursor + timedelta(days=max(7, round(weeks * 7)))

        focus: dict[str, float] = {}
        for item in bucket:
            for skill_id, weight in item.skills.items():
                focus[skill_id] = focus.get(skill_id, 0.0) + weight
        top_focus = [s for s, _ in sorted(focus.items(), key=lambda kv: -kv[1])[:4]]

        milestones.append(
            Milestone(
                index=index + 1,
                title=_phase_title(catalog, bucket, index, len(buckets)),
                focus_skills=top_focus,
                items=bucket,
                hours=hours,
                weeks=weeks,
                starts_on=cursor.isoformat(),
                ends_on=ends.isoformat(),
            )
        )
        cursor = ends
    return milestones


# Skill categories that describe end-of-journey activity rather than material
# to learn. Interview prep before you know the material is wasted effort.
_LATE_CATEGORIES = {"Career"}


def _learning_order(priority: dict[str, float], catalog: Catalog):
    """Ordering policy for items that are all ready at the same time.

    Prerequisite edges are sparse: most pairs of items have no edge between
    them, so topological sort alone leaves the order to the tie-break. Ranking
    priority is the wrong tie-break on its own, because it measures how much
    gap an item closes, not when it makes sense to study it — that is how Git
    fundamentals ended up in the final milestone and a SQL course ahead of
    introductory Python.

    Sequence by, in order: career-stage material last, then difficulty level,
    then prerequisite depth, then ranking priority.
    """

    def category_stage(item_id: str) -> int:
        item = catalog.items[item_id]
        if not item.skills:
            return 0
        dominant = max(item.skills.items(), key=lambda kv: kv[1])[0]
        skill = catalog.skills.get(dominant)
        return 1 if skill and skill.category in _LATE_CATEGORIES else 0

    def key(item_id: str) -> tuple:
        item = catalog.items[item_id]
        return (
            category_stage(item_id),
            item.level,
            item.depth,
            -priority.get(item_id, 0.0),
            item_id,
        )

    return key


def _ensure_projects(
    profile: LearnerProfile,
    selected: dict[str, ScoredItem],
    recommender: Recommender,
    level: float,
    gaps: dict[str, float],
    catalog: Catalog,
) -> None:
    """Guarantee the path contains hands-on work, in place.

    Coverage-per-hour is a good objective but it has a blind spot: a 20-hour
    project that consolidates four skills a learner has already been taught
    scores worse than two 10-hour courses that each introduce a new one. Left
    alone the planner produces a reading list, not a portfolio. We top up to
    MIN_PROJECTS with the best-scoring projects that serve the goal.

    "Serve the goal" is the binding constraint, not a preference. A project
    that covers none of the outstanding gap is not hands-on practice for this
    learner, it is a detour — offline evaluation caught a security analyst
    being handed "Ship a Mobile App to Store" purely to satisfy the quota.
    Where the catalog offers no on-goal project, the honest move is to leave
    the path shorter rather than pad it.
    """
    have = sum(1 for i in selected if catalog.items[i].kind == "project")
    if have >= MIN_PROJECTS:
        return

    project_ids = {i for i, item in catalog.items.items() if item.kind == "project"}
    ranked = recommender.recommend(
        profile, gaps, level, k=(MIN_PROJECTS - have) * 4,
        exclude=set(selected), candidates=project_ids,
    )
    added = 0
    for candidate in ranked:
        if added >= MIN_PROJECTS - have:
            break
        if sum(candidate.covers.values()) <= 0:
            continue
        selected[candidate.item_id] = candidate
        added += 1


def _to_path_item(item_id: str, catalog: Catalog, scored: ScoredItem | None, filler: bool) -> PathItem:
    item = catalog.items[item_id]
    return PathItem(
        item_id=item.id,
        title=item.title,
        kind=item.kind,
        provider=item.provider,
        hours=item.hours,
        level=item.level,
        modality=item.modality,
        skills=item.skills,
        prereqs=item.prereqs,
        rating=item.rating,
        reason_components=scored.contributions if scored else {},
        covers=scored.covers if scored else {},
        is_prerequisite_fill=filler,
    )


def generate_path(
    profile: LearnerProfile,
    catalog: Catalog = CATALOG,
    recommender: Recommender = RECOMMENDER,
    max_items: int = MAX_SELECTED,
    start: date | None = None,
) -> LearningPath:
    """Build a complete, ordered, scheduled learning path for a learner."""
    start = start or date.today()

    mastery, confidence = compute_mastery(profile, catalog)
    level = implied_level(profile, mastery)
    gaps = analyse_gaps(profile, mastery, confidence, catalog)
    initial_gap = gap_vector(gaps)
    initial_mass = sum(initial_gap.values())
    readiness_before = readiness(profile, mastery, catalog)

    simulated = dict(mastery)
    remaining = dict(initial_gap)
    selected: dict[str, ScoredItem] = {}
    covered_mass = 0.0

    while remaining and len(selected) < max_items:
        if initial_mass and covered_mass / initial_mass >= COVERAGE_TARGET:
            break

        ranked = recommender.recommend(
            profile,
            remaining,
            level,
            k=12,
            exclude=set(selected),
        )
        if not ranked:
            break

        # Re-rank the shortlist by marginal gap coverage per unit of effort.
        best, best_efficiency = None, -1.0
        for candidate in ranked:
            gain = sum(candidate.covers.values())
            if gain <= 0:
                continue
            candidate_item = catalog.items[candidate.item_id]
            hours = max(1, candidate_item.hours)
            bonus = KIND_BONUS.get(candidate_item.kind, 1.0)
            efficiency = (gain * candidate.score * bonus) / (hours ** COST_EXPONENT)
            if efficiency > best_efficiency:
                best, best_efficiency = candidate, efficiency

        if best is None:
            break

        selected[best.item_id] = best
        item = catalog.items[best.item_id]
        _simulate_gain(simulated, item.skills, item.level)

        # Recompute the outstanding gap against simulated mastery.
        for skill_id in list(remaining):
            target_value = next((g.target for g in gaps if g.skill_id == skill_id), 0.0)
            shortfall = max(0.0, target_value - simulated.get(skill_id, 0.0))
            new_weighted = shortfall * target_value
            covered_mass += max(0.0, remaining[skill_id] - new_weighted)
            if new_weighted <= 1e-4:
                del remaining[skill_id]
            else:
                remaining[skill_id] = new_weighted

    _ensure_projects(profile, selected, recommender, level, initial_gap, catalog)

    # Close under prerequisites so the path is actually followable.
    fillers = prerequisite_closure(set(selected), catalog, known=profile.completed_ids)
    fillers -= set(selected)

    everything = set(selected) | fillers
    priority = {item_id: scored.score for item_id, scored in selected.items()}
    for filler in fillers:
        priority.setdefault(filler, 0.0)

    # A prerequisite is exactly as urgent as the most urgent thing it unlocks.
    # Without this, a filler course sorts to the back of the path on its own
    # (zero) priority and drags the high-value item that needs it along with
    # it, so foundational material ends up scheduled after what builds on it.
    changed = True
    while changed:
        changed = False
        for item_id in everything:
            for prereq in catalog.items[item_id].prereqs:
                if prereq in everything and priority[prereq] < priority[item_id]:
                    priority[prereq] = priority[item_id]
                    changed = True

    ordered_ids = topological_order(
        everything, priority, catalog, sort_key=_learning_order(priority, catalog)
    )

    ordered = [
        _to_path_item(item_id, catalog, selected.get(item_id), item_id in fillers)
        for item_id in ordered_ids
    ]

    milestones = _chunk_into_milestones(ordered, profile.hours_per_week, catalog, start)
    total_hours = sum(item.hours for item in ordered)

    # Readiness the learner would reach on finishing the path.
    projected = dict(mastery)
    for item in ordered:
        _simulate_gain(projected, item.skills, item.level)
    readiness_after = readiness(profile, projected, catalog)

    role = catalog.roles.get(profile.role_id) if profile.role_id else None
    if role is not None:
        title = role.title
    elif profile.goal_skills:
        # No career role, but they named skills — title the path after them so
        # the header reads as a goal rather than as a blank.
        named = [
            catalog.skill_name(s)
            for s, _ in sorted(profile.goal_skills.items(), key=lambda kv: -kv[1])[:2]
        ]
        title = " & ".join(named)
    else:
        title = None

    return LearningPath(
        profile_id=profile.id,
        goal_text=profile.goal_text,
        role_id=profile.role_id,
        role_title=title,
        milestones=milestones,
        total_hours=total_hours,
        total_weeks=round(total_hours / max(1.0, profile.hours_per_week), 1),
        coverage=round(covered_mass / initial_mass, 4) if initial_mass else 0.0,
        gap_count=len(gaps),
        readiness_before=readiness_before,
        readiness_after=readiness_after,
        gap_summary=[
            {
                "skill_id": g.skill_id,
                "name": g.name,
                "category": g.category,
                "target": g.target,
                "mastery": g.mastery,
                "gap": g.gap,
                "confidence": g.confidence,
            }
            for g in gaps[:12]
        ],
        generated_on=start.isoformat(),
    )
