"""Hybrid recommendation engine.

No single signal is trustworthy on its own. Content similarity alone ignores
what the learner still needs; pure gap coverage recommends whatever teaches
the most skills regardless of quality or fit; collaborative filtering alone
cannot serve a learner with no history (cold start) and just echoes what is
popular. PathFinder scores every candidate on six independent components and
combines them linearly:

  coverage   how much of the learner's *remaining weighted skill gap* the item
             closes. This is the primary signal and the one tied to the goal.
  semantic   cosine similarity between the goal text and the item, in the
             shared LSA space. Catches intent the role target misses.
  collab     item-item collaborative filtering over the interaction log:
             "learners who completed what you completed also took this".
  level fit  a Gaussian penalty on the distance between item difficulty and
             the learner's estimated level — the anti-frustration term.
  quality    Bayesian-smoothed rating blended with log-popularity, so a 4.9
             rated by 200 people does not outrank a 4.8 rated by 200,000.
  modality   agreement with the learner's stated format preference.

Keeping the components separate is what makes the recommendations explainable:
the same numbers that produce the ranking are handed to the explanation layer
as attributions, so "why this course" is answered from the actual arithmetic
rather than from a plausible-sounding story generated after the fact.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from app.ml.embeddings import SPACE, SemanticSpace
from app.ml.graph import missing_prerequisites
from app.ml.profiler import LearnerProfile
from app.store import CATALOG, Catalog

# Component weights. They sum to 1.0 so the final score stays interpretable.
WEIGHTS = {
    "coverage": 0.38,
    "semantic": 0.18,
    "collab": 0.14,
    "level_fit": 0.12,
    "quality": 0.10,
    "modality": 0.08,
}

# Bayesian prior for rating smoothing: a global mean and its equivalent count.
PRIOR_RATING = 4.6
PRIOR_COUNT = 50_000.0

# Shrinkage for co-occurrence similarity — damps pairs seen only a few times.
CF_SHRINKAGE = 12.0

# Width of the level-fit Gaussian, in level units.
LEVEL_TOLERANCE = 0.85

# Penalty multiplier applied per unmet prerequisite when ranking non-ready items.
PREREQ_PENALTY = 0.12


@dataclass
class ScoredItem:
    """A candidate with its score decomposed into the contributing signals."""

    item_id: str
    score: float
    components: dict[str, float] = field(default_factory=dict)
    contributions: dict[str, float] = field(default_factory=dict)
    covers: dict[str, float] = field(default_factory=dict)
    missing_prereqs: list[str] = field(default_factory=list)

    @property
    def is_ready(self) -> bool:
        return not self.missing_prereqs

    def top_component(self) -> str:
        """The signal that contributed most to this item's score."""
        if not self.contributions:
            return "coverage"
        return max(self.contributions.items(), key=lambda kv: kv[1])[0]


class Recommender:
    """Scores catalog items against a learner profile and skill gaps."""

    def __init__(self, catalog: Catalog = CATALOG, space: SemanticSpace = SPACE) -> None:
        self.catalog = catalog
        self.space = space
        self._build_cf_matrix()
        self._build_quality_prior()

    # -- offline fitting ----------------------------------------------------

    def _build_cf_matrix(self) -> None:
        """Item-item cosine similarity over the co-occurrence counts.

        sim(a, b) = co(a, b) / sqrt(n(a) * n(b)), then shrunk toward zero by
        co / (co + lambda) so that a pair observed twice is not treated as
        confidently as a pair observed two hundred times.
        """
        item_ids = self.catalog.item_ids
        index = self.catalog.item_index
        size = len(item_ids)

        counts = self.catalog.interactions.get("item_counts", {})
        co_counts = self.catalog.interactions.get("co_counts", {})

        matrix = np.zeros((size, size), dtype=np.float32)
        for a, partners in co_counts.items():
            if a not in index:
                continue
            n_a = counts.get(a, 0)
            if not n_a:
                continue
            row = index[a]
            for b, co in partners.items():
                if b not in index:
                    continue
                n_b = counts.get(b, 0)
                if not n_b:
                    continue
                similarity = co / math.sqrt(n_a * n_b)
                matrix[row, index[b]] = similarity * (co / (co + CF_SHRINKAGE))

        np.fill_diagonal(matrix, 0.0)
        self.cf_matrix = matrix

    def _build_quality_prior(self) -> None:
        """Bayesian-smoothed rating blended with log-scaled popularity."""
        scores = np.zeros(len(self.catalog.item_ids), dtype=np.float32)
        max_log_learners = math.log1p(
            max(item.learners for item in self.catalog.items.values())
        )
        for item_id, idx in self.catalog.item_index.items():
            item = self.catalog.items[item_id]
            smoothed = (
                (item.rating * item.learners + PRIOR_RATING * PRIOR_COUNT)
                / (item.learners + PRIOR_COUNT)
            )
            # Map a 3.5-5.0 rating range onto 0..1.
            rating_score = max(0.0, min(1.0, (smoothed - 3.5) / 1.5))
            popularity = math.log1p(item.learners) / max_log_learners
            scores[idx] = 0.7 * rating_score + 0.3 * popularity
        self.quality = scores

    # -- scoring ------------------------------------------------------------

    def _collab_scores(self, completed: set[str]) -> np.ndarray:
        """Sum of CF similarity from each completed item, normalised to 0..1."""
        size = len(self.catalog.item_ids)
        if not completed:
            return np.zeros(size, dtype=np.float32)
        rows = [self.catalog.item_index[i] for i in completed if i in self.catalog.item_index]
        if not rows:
            return np.zeros(size, dtype=np.float32)
        raw = self.cf_matrix[rows].sum(axis=0)
        peak = float(raw.max())
        return raw / peak if peak > 0 else raw

    def _goal_vector(self, profile: LearnerProfile) -> np.ndarray | None:
        """How the learner's goal is represented for semantic matching.

        Free text wins whenever it exists and means something to the catalog:
        it carries intent the role label cannot ("switching from web dev", "for
        research, not industry"). Only when there is no usable text do we fall
        back to the chosen role's own vector.

        That fallback is not cosmetic. A learner who selects a role from a
        button leaves `goal_text` empty, and the previous code read that as
        "no goal", zeroing the semantic component for every candidate — 0.18 of
        the ranking weight silently discarded on what is the most common route
        through the product. The role is a perfectly good statement of intent;
        it just arrives as an id instead of a sentence.

        Deliberately not done: writing the role title into `profile.goal_text`.
        That would duplicate state, and would make the profile claim the
        learner said something they never typed.
        """
        if profile.goal_text:
            vector = self.space.encode(profile.goal_text)
            if not self.space.is_empty(vector):
                return vector
        if profile.role_id:
            return self.space.role_vector(profile.role_id)
        return None

    def _coverage_score(self, item_skills: dict[str, float], gaps: dict[str, float]) -> tuple[float, dict[str, float]]:
        """How much of the outstanding weighted gap this item addresses."""
        covers = {
            skill_id: round(weight * gaps[skill_id], 4)
            for skill_id, weight in item_skills.items()
            if skill_id in gaps
        }
        return sum(covers.values()), covers

    def recommend(
        self,
        profile: LearnerProfile,
        gaps: dict[str, float],
        learner_level: float,
        k: int = 10,
        exclude: set[str] | None = None,
        ready_only: bool = False,
        candidates: set[str] | None = None,
    ) -> list[ScoredItem]:
        """Rank catalog items for this learner, best first."""
        exclude = (exclude or set()) | profile.completed_ids
        completed = profile.completed_ids

        goal_vector = self._goal_vector(profile)
        semantic = (
            self.space.similar_items(goal_vector)
            if goal_vector is not None and not self.space.is_empty(goal_vector)
            else np.zeros(len(self.catalog.item_ids))
        )
        collab = self._collab_scores(completed)

        # Normalise coverage across candidates so weights stay comparable.
        raw_coverage: dict[str, tuple[float, dict[str, float]]] = {}
        pool = candidates if candidates is not None else set(self.catalog.items)
        for item_id in pool:
            if item_id in exclude:
                continue
            item = self.catalog.items[item_id]
            raw_coverage[item_id] = self._coverage_score(item.skills, gaps)
        peak_coverage = max((v[0] for v in raw_coverage.values()), default=0.0) or 1.0

        preferred = set(profile.preferred_modalities)
        scored: list[ScoredItem] = []

        for item_id, (coverage_raw, covers) in raw_coverage.items():
            item = self.catalog.items[item_id]
            idx = self.catalog.item_index[item_id]

            missing = missing_prerequisites(item_id, completed, self.catalog)
            if ready_only and missing:
                continue

            level_delta = item.level - learner_level
            components = {
                "coverage": coverage_raw / peak_coverage,
                "semantic": max(0.0, float(semantic[idx])),
                "collab": float(collab[idx]),
                "level_fit": math.exp(-(level_delta ** 2) / (2 * LEVEL_TOLERANCE ** 2)),
                "quality": float(self.quality[idx]),
                "modality": 1.0 if not preferred else (1.0 if item.modality in preferred else 0.35),
            }

            contributions = {name: WEIGHTS[name] * value for name, value in components.items()}
            score = sum(contributions.values())

            # Items with unmet prerequisites are still rankable — the planner
            # will pull their prerequisites in — but they are not immediate
            # next actions, so they are discounted rather than dropped.
            if missing:
                score *= max(0.4, 1.0 - PREREQ_PENALTY * len(missing))

            scored.append(
                ScoredItem(
                    item_id=item_id,
                    score=round(score, 5),
                    components={k_: round(v, 4) for k_, v in components.items()},
                    contributions={k_: round(v, 4) for k_, v in contributions.items()},
                    covers=covers,
                    missing_prereqs=missing,
                )
            )

        scored.sort(key=lambda s: (-s.score, s.item_id))
        return scored[:k]

    def diversify(
        self, scored: list[ScoredItem], k: int, lambda_: float = 0.72
    ) -> list[ScoredItem]:
        """Maximal-marginal-relevance re-ranking.

        Straight score ordering tends to return five near-identical courses
        that all teach the same top-gap skill. MMR trades a little relevance
        for coverage breadth: each pick is penalised by its maximum semantic
        similarity to what has already been picked.
        """
        if not scored:
            return []
        chosen: list[ScoredItem] = [scored[0]]
        pool = scored[1:]

        while pool and len(chosen) < k:
            best, best_value = None, -1e9
            chosen_rows = [self.catalog.item_index[c.item_id] for c in chosen]
            chosen_vectors = self.space.item_vectors[chosen_rows]
            for candidate in pool:
                vector = self.space.item_vectors[self.catalog.item_index[candidate.item_id]]
                redundancy = float(np.max(chosen_vectors @ vector))
                value = lambda_ * candidate.score - (1 - lambda_) * redundancy
                if value > best_value:
                    best, best_value = candidate, value
            chosen.append(best)
            pool.remove(best)

        return chosen


RECOMMENDER = Recommender()
