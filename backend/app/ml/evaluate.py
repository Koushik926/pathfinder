"""Offline evaluation: how good are these paths, and how do we know?

A test suite proves the system does what it was told. It says nothing about
whether what it was told is any good. This module answers the second question.

Learning-path recommendation cannot borrow the usual recommender metrics.
Precision, recall and NDCG all assume a held-out set of items the user
*would have chosen*, and score you on reproducing that choice. A learning path
is not a prediction of what someone would pick — it is a claim about what will
get them to a goal fastest, in an order they can actually follow. Ranking the
courses a learner already likes is the opposite of useful.

So the metrics here measure the thing the system actually claims:

  readiness_gain        importance-weighted progress toward the goal, if the
                        learner completes every item they are handed
  achievable_gain       the same, counting only items the learner can actually
                        reach — one whose prerequisites are unmet when it comes
                        up is a wall, not a lesson, and the gain behind it never
                        arrives. This is the honest headline number, and the
                        gap between it and readiness_gain is how much of a
                        strategy's promised progress is fictional
  gain_per_100h         achievable gain per unit of the learner's time — the
                        efficiency number, and the one that matters most,
                        since every learner's real budget is hours not items
  prerequisite_validity fraction of items whose prerequisites are met by the
                        time they are scheduled. Anything below 1.0 is a path
                        that cannot be followed as written
  redundancy            fraction of *chosen* items teaching nothing the learner
                        lacks — wasted time, straightforwardly
  scaffolding           fraction of items pulled in only to unlock something
                        else. These also teach nothing new toward the goal, but
                        they are the price of a followable path, so they are
                        reported separately rather than counted as waste
  applied_rate          fraction of paths containing at least two projects or
                        assessments — you do not become job-ready by watching
  catalog_coverage      distinct items used across the whole cohort, which
                        catches the failure where every learner is handed the
                        same five popular courses

Each is computed over a synthetic cohort with *known* skill gaps — the standard
validation design in the learning-path literature, since real learners do not
come with ground-truth mastery labels.

Four strategies are measured against each other on identical learners and an
identical hour budget, so differences are attributable to selection, not spend:

  popularity     rank by rating and enrolment. The naive baseline.
  semantic       rank by similarity to the goal text. An embedding-only or
                 LLM-only system with no learner model behaves like this.
  coverage_only  greedy gap coverage, but no prerequisite closure and no
                 pedagogical ordering. This is the ablation that isolates
                 what the graph contributes.
  pathfinder     the full system.

Run it with ``python -m app.ml.evaluate`` or via ``scripts/evaluate.py``.
"""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass, field, asdict

from app.ml.gap import analyse_gaps, gap_vector, readiness
from app.ml.graph import missing_prerequisites, prerequisite_closure, topological_order
from app.ml.planner import _simulate_gain, generate_path
from app.ml.profiler import Completion, LearnerProfile, compute_mastery, implied_level
from app.ml.recommender import RECOMMENDER, Recommender
from app.store import CATALOG, Catalog

COHORT_SIZE = 60
SEED = 20260907


# ---------------------------------------------------------------- cohort ----

@dataclass
class SyntheticLearner:
    """A learner with a known history, and therefore a known ground-truth gap."""

    id: str
    role_id: str
    goal_text: str
    experience_level: int
    hours_per_week: float
    completed: list[str]

    def profile(self) -> LearnerProfile:
        return LearnerProfile(
            id=self.id,
            goal_text=self.goal_text,
            role_id=self.role_id,
            experience_level=self.experience_level,
            hours_per_week=self.hours_per_week,
            completed=[Completion(item_id=i, months_ago=6.0) for i in self.completed],
        )


def build_cohort(
    size: int = COHORT_SIZE, seed: int = SEED, catalog: Catalog = CATALOG
) -> list[SyntheticLearner]:
    """Sample learners across every role, at every level, with valid histories.

    A history is only realistic if it is prerequisite-closed: nobody has
    finished Advanced PyTorch without finishing Python. Sampling a random
    subset of items would produce learners the real world never sends us, and
    flatter the graph-aware strategy for the wrong reason.
    """
    rng = random.Random(seed)
    role_ids = sorted(catalog.roles)
    item_ids = sorted(catalog.items)
    cohort: list[SyntheticLearner] = []

    for index in range(size):
        role = catalog.roles[role_ids[index % len(role_ids)]]
        level = 1 + index % 3
        # A third of the cohort are cold starts: no history at all.
        history_size = 0 if index % 3 == 0 else rng.randint(1, 6 * level)

        completed: set[str] = set()
        for _ in range(history_size):
            seed_item = rng.choice(item_ids)
            # Take the item and everything it depends on, so the history is
            # internally consistent.
            completed |= prerequisite_closure({seed_item}, catalog, known=completed)
            completed.add(seed_item)

        cohort.append(
            SyntheticLearner(
                id=f"eval-{index:03d}",
                role_id=role.id,
                goal_text=role.title,
                experience_level=level,
                hours_per_week=float(rng.choice([3, 5, 8, 10, 15, 20])),
                completed=sorted(completed),
            )
        )
    return cohort


# --------------------------------------------------------------- metrics ----

@dataclass
class PathMetrics:
    readiness_before: float
    readiness_after: float
    readiness_gain: float
    achievable_gain: float
    gain_per_100h: float
    prerequisite_validity: float
    redundancy: float
    scaffolding: float
    hours: int
    items: int
    applied_items: int


def score_path(
    learner: SyntheticLearner,
    ordered_items: list[str],
    catalog: Catalog = CATALOG,
    scaffold_ids: set[str] | None = None,
) -> PathMetrics:
    """Measure one ordered list of items for one learner.

    Deliberately knows nothing about which strategy produced the list, so
    every strategy is judged by exactly the same instrument.
    """
    scaffold_ids = scaffold_ids or set()
    profile = learner.profile()
    mastery, confidence = compute_mastery(profile, catalog)
    before = readiness(profile, mastery, catalog)
    gaps = analyse_gaps(profile, mastery, confidence, catalog)
    outstanding = gap_vector(gaps)

    simulated = dict(mastery)
    # A second, stricter simulation: the learner walks the path in order and
    # stops crediting anything they were never able to start.
    achievable = dict(mastery)
    completed_so_far = set(learner.completed)
    reachable = set(learner.completed)
    satisfied = 0
    redundant = 0
    scaffold = 0
    hours = 0
    applied = 0

    for item_id in ordered_items:
        item = catalog.items[item_id]
        # Followable: are this item's prerequisites met at the moment it is
        # scheduled, given the history plus everything scheduled before it?
        if not missing_prerequisites(item_id, completed_so_far, catalog):
            satisfied += 1
        # Reachability is tracked against what the learner has actually been
        # able to finish, not against everything that was merely listed.
        if not missing_prerequisites(item_id, reachable, catalog):
            _simulate_gain(achievable, item.skills, item.level)
            reachable.add(item_id)
        # Useful: does it teach anything still outstanding? An item that does
        # not, but that unlocks a later item that does, is scaffolding rather
        # than waste — strategies without a prerequisite graph have none of it,
        # so this split never flatters them.
        if not any(skill_id in outstanding for skill_id in item.skills):
            if item_id in scaffold_ids:
                scaffold += 1
            else:
                redundant += 1

        _simulate_gain(simulated, item.skills, item.level)
        completed_so_far.add(item_id)
        hours += item.hours
        if item.kind in ("project", "assessment"):
            applied += 1

    after = readiness(profile, simulated, catalog)
    after_achievable = readiness(profile, achievable, catalog)
    count = len(ordered_items)
    gain = round(after - before, 4)
    real_gain = round(after_achievable - before, 4)

    return PathMetrics(
        readiness_before=before,
        readiness_after=after,
        readiness_gain=gain,
        achievable_gain=real_gain,
        gain_per_100h=round(100.0 * real_gain / hours, 4) if hours else 0.0,
        prerequisite_validity=round(satisfied / count, 4) if count else 1.0,
        redundancy=round(redundant / count, 4) if count else 0.0,
        scaffolding=round(scaffold / count, 4) if count else 0.0,
        hours=hours,
        items=count,
        applied_items=applied,
    )


# ------------------------------------------------------------ strategies ----

def strategy_pathfinder(learner: SyntheticLearner, budget: int | None, catalog, recommender):
    path = generate_path(learner.profile(), catalog, recommender)
    return [item.item_id for item in path.all_items]


def scaffold_of(learner: SyntheticLearner, catalog, recommender) -> set[str]:
    """Which of PathFinder's items were pulled in only to unlock others."""
    path = generate_path(learner.profile(), catalog, recommender)
    return {i.item_id for i in path.all_items if i.is_prerequisite_fill}


def _take_within_budget(candidates: list[str], budget: int | None, catalog: Catalog) -> list[str]:
    if budget is None:
        return candidates
    chosen, spent = [], 0
    for item_id in candidates:
        hours = catalog.items[item_id].hours
        if spent + hours > budget:
            continue
        chosen.append(item_id)
        spent += hours
    return chosen


def strategy_popularity(learner: SyntheticLearner, budget: int | None, catalog, recommender):
    """Rank by rating and enrolment — no learner model at all."""
    known = set(learner.completed)
    ranked = sorted(
        (i for i in catalog.items.values() if i.id not in known),
        key=lambda i: (-(i.rating * (i.learners ** 0.25)), i.id),
    )
    return _take_within_budget([i.id for i in ranked], budget, catalog)


def strategy_semantic(learner: SyntheticLearner, budget: int | None, catalog, recommender):
    """Rank by similarity to the goal text — an embedding-only system."""
    known = set(learner.completed)
    vector = recommender.space.encode(learner.goal_text)
    scores = recommender.space.similar_items(vector)
    ranked = sorted(
        (i for i in catalog.items.values() if i.id not in known),
        key=lambda i: (-float(scores[catalog.item_index[i.id]]), i.id),
    )
    return _take_within_budget([i.id for i in ranked], budget, catalog)


def strategy_coverage_only(learner: SyntheticLearner, budget: int | None, catalog, recommender):
    """Greedy gap coverage per hour, with no prerequisite graph.

    The ablation: same objective as PathFinder, none of the sequencing. What
    it loses relative to the full system is exactly what the graph buys.
    """
    profile = learner.profile()
    mastery, confidence = compute_mastery(profile, catalog)
    gaps = analyse_gaps(profile, mastery, confidence, catalog)
    remaining = gap_vector(gaps)
    known = set(learner.completed)

    simulated = dict(mastery)
    chosen: list[str] = []
    spent = 0

    while remaining:
        best, best_efficiency = None, 0.0
        for item in catalog.items.values():
            if item.id in known or item.id in chosen:
                continue
            if budget is not None and spent + item.hours > budget:
                continue
            gain = sum(w * remaining.get(s, 0.0) for s, w in item.skills.items())
            efficiency = gain / max(1, item.hours)
            if efficiency > best_efficiency:
                best, best_efficiency = item, efficiency
        if best is None:
            break
        chosen.append(best.id)
        spent += best.hours
        _simulate_gain(simulated, best.skills, best.level)
        for gap in gaps:
            shortfall = max(0.0, gap.target - simulated.get(gap.skill_id, 0.0))
            weighted = shortfall * gap.target
            if weighted <= 1e-4:
                remaining.pop(gap.skill_id, None)
            elif gap.skill_id in remaining:
                remaining[gap.skill_id] = weighted
    return chosen


STRATEGIES = {
    "popularity": strategy_popularity,
    "semantic": strategy_semantic,
    "coverage_only": strategy_coverage_only,
    "pathfinder": strategy_pathfinder,
}


# ------------------------------------------------------------------ run -----

@dataclass
class StrategyReport:
    strategy: str
    learners: int
    readiness_gain: float
    achievable_gain: float
    gain_per_100h: float
    prerequisite_validity: float
    redundancy: float
    scaffolding: float
    applied_rate: float
    catalog_coverage: int
    mean_hours: float
    cold_start_gain: float
    per_learner: list[dict] = field(default_factory=list)


def _mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0


def run(
    size: int = COHORT_SIZE,
    seed: int = SEED,
    catalog: Catalog = CATALOG,
    recommender: Recommender = RECOMMENDER,
    keep_detail: bool = False,
) -> dict:
    cohort = build_cohort(size, seed, catalog)

    # PathFinder runs first so its hour spend becomes the budget every other
    # strategy is held to. Comparing at equal cost is the only fair test: a
    # baseline that recommends 400 hours of content will always "cover" more.
    budgets: dict[str, int] = {}
    results: dict[str, list[tuple[SyntheticLearner, list[str], PathMetrics]]] = {}

    for name in ("pathfinder", "popularity", "semantic", "coverage_only"):
        strategy = STRATEGIES[name]
        rows = []
        for learner in cohort:
            budget = budgets.get(learner.id) if name != "pathfinder" else None
            items = strategy(learner, budget, catalog, recommender)
            fills = scaffold_of(learner, catalog, recommender) if name == "pathfinder" else set()
            metrics = score_path(learner, items, catalog, scaffold_ids=fills)
            if name == "pathfinder":
                budgets[learner.id] = metrics.hours
            rows.append((learner, items, metrics))
        results[name] = rows

    reports: dict[str, StrategyReport] = {}
    for name, rows in results.items():
        used: set[str] = set()
        for _, items, _ in rows:
            used |= set(items)
        cold = [m.achievable_gain for learner, _, m in rows if not learner.completed]
        reports[name] = StrategyReport(
            strategy=name,
            learners=len(rows),
            readiness_gain=_mean([m.readiness_gain for _, _, m in rows]),
            achievable_gain=_mean([m.achievable_gain for _, _, m in rows]),
            gain_per_100h=_mean([m.gain_per_100h for _, _, m in rows]),
            prerequisite_validity=_mean([m.prerequisite_validity for _, _, m in rows]),
            redundancy=_mean([m.redundancy for _, _, m in rows]),
            scaffolding=_mean([m.scaffolding for _, _, m in rows]),
            applied_rate=_mean([1.0 if m.applied_items >= 2 else 0.0 for _, _, m in rows]),
            catalog_coverage=len(used),
            mean_hours=_mean([float(m.hours) for _, _, m in rows]),
            cold_start_gain=_mean(cold),
            per_learner=(
                [{"learner": l.id, "role": l.role_id, **asdict(m)} for l, _, m in rows]
                if keep_detail else []
            ),
        )

    return {
        "cohort_size": len(cohort),
        "seed": seed,
        "catalog": {
            "items": len(catalog.items),
            "skills": len(catalog.skills),
            "roles": len(catalog.roles),
        },
        "strategies": {name: asdict(report) for name, report in reports.items()},
    }


def format_report(result: dict) -> str:
    """A table a human can read out loud in a panel."""
    columns = [
        ("readiness_gain", "Gain (if perfect)", "{:.3f}"),
        ("achievable_gain", "Gain (achievable)", "{:.3f}"),
        ("gain_per_100h", "Gain / 100h", "{:.3f}"),
        ("prerequisite_validity", "Prereq validity", "{:.1%}"),
        ("redundancy", "Wasted items", "{:.1%}"),
        ("scaffolding", "Scaffolding", "{:.1%}"),
        ("applied_rate", "Has 2+ projects", "{:.1%}"),
        ("catalog_coverage", "Distinct items", "{:d}"),
        ("mean_hours", "Mean hours", "{:.0f}"),
        ("cold_start_gain", "Cold-start gain", "{:.3f}"),
    ]
    order = ["popularity", "semantic", "coverage_only", "pathfinder"]
    width = 18

    lines = [
        f"PathFinder offline evaluation — {result['cohort_size']} synthetic learners, "
        f"seed {result['seed']}",
        f"catalog: {result['catalog']['items']} items, {result['catalog']['skills']} skills, "
        f"{result['catalog']['roles']} roles",
        "",
        "metric".ljust(width) + "".join(name.rjust(15) for name in order),
        "-" * (width + 15 * len(order)),
    ]
    for key, label, fmt in columns:
        row = label.ljust(width)
        for name in order:
            row += fmt.format(result["strategies"][name][key]).rjust(15)
        lines.append(row)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate PathFinder against baselines.")
    parser.add_argument("--size", type=int, default=COHORT_SIZE)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--json", metavar="PATH", help="also write the raw result here")
    parser.add_argument("--detail", action="store_true", help="include per-learner rows in JSON")
    args = parser.parse_args()

    result = run(size=args.size, seed=args.seed, keep_detail=args.detail)
    print(format_report(result))
    if args.json:
        with open(args.json, "w") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print(f"\nraw result -> {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
