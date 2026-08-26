"""Semantic space shared by items, skills, roles and free-text learner goals.

Approach: TF-IDF over a hand-built document per catalog entity, reduced with
truncated SVD to a dense 128-dimensional space (latent semantic analysis),
then L2-normalised so cosine similarity is a plain dot product.

Two feature views are unioned before the SVD:

  word  1-2 gram word TF-IDF, carrying most of the topical signal.
  char  3-5 gram character TF-IDF within word boundaries. This is what makes
        free-text goals robust: a learner types "designing websites", neither
        form of which appears in the catalog, and the character view still
        matches it to "web design" through shared n-grams. A word-only model
        returns a zero vector for such a query and recommends nothing.

Why LSA rather than a neural sentence encoder: the whole model is a few MB,
fits in under a second, is fully deterministic, and needs no model download —
a judge can clone the repo and run it completely offline. The SVD also gives
genuine synonymy handling that raw TF-IDF lacks: "neural networks" and "deep
learning" land near each other because they co-occur across the corpus.
"""

from __future__ import annotations

import re

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion

from app.store import CATALOG, Catalog

N_COMPONENTS = 128
RANDOM_STATE = 20260826

# Minimum cosine for a free-text goal to be accepted as naming a role.
ROLE_MATCH_THRESHOLD = 0.30
# Minimum cosine for an inferred (not explicitly named) skill.
SKILL_MATCH_THRESHOLD = 0.22
# Inferred skills must also score within this fraction of the best match,
# which suppresses the long tail of weakly-related skills.
SKILL_RELATIVE_CUTOFF = 0.55


def _normalise_rows(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / np.maximum(norms, 1e-9)


def _build_vectorizer() -> FeatureUnion:
    word = TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=1,
        max_df=0.85,
        strip_accents="unicode",
        token_pattern=r"[a-z0-9+#.]{2,}",
    )
    char = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        sublinear_tf=True,
        min_df=2,
        max_df=0.90,
        strip_accents="unicode",
    )
    # The word view stays dominant; characters are a morphological safety net.
    return FeatureUnion(
        [("word", word), ("char", char)],
        transformer_weights={"word": 1.0, "char": 0.55},
    )


class SemanticSpace:
    """Fits the shared latent space and projects new text into it."""

    def __init__(self, catalog: Catalog = CATALOG) -> None:
        self.catalog = catalog

        item_docs = [catalog.item_text(catalog.items[i]) for i in catalog.item_ids]
        skill_docs = [catalog.skill_text(catalog.skills[s]) for s in catalog.skill_ids]
        self.role_ids = sorted(catalog.roles)
        role_docs = [self._role_text(catalog, rid) for rid in self.role_ids]

        corpus = item_docs + skill_docs + role_docs

        self.vectorizer = _build_vectorizer()
        sparse = self.vectorizer.fit_transform(corpus)

        # SVD needs strictly fewer components than features and samples.
        n_components = min(N_COMPONENTS, sparse.shape[1] - 1, sparse.shape[0] - 1)
        self.svd = TruncatedSVD(n_components=n_components, random_state=RANDOM_STATE)
        dense = _normalise_rows(self.svd.fit_transform(sparse))

        n_items, n_skills = len(item_docs), len(skill_docs)
        self.item_vectors = dense[:n_items]
        self.skill_vectors = dense[n_items:n_items + n_skills]
        self.role_vectors = dense[n_items + n_skills:]

        self.explained_variance = float(self.svd.explained_variance_ratio_.sum())
        self.n_components = n_components
        self.n_features = sparse.shape[1]

        # Alias tables, for exact matching ahead of any cosine fallback.
        self._skill_aliases: dict[str, str] = {}
        for skill in catalog.skills.values():
            for phrase in [skill.name, skill.id.replace("-", " "), *skill.aliases]:
                self._skill_aliases[self._canon(phrase)] = skill.id
        self._role_aliases: dict[str, str] = {}
        for role in catalog.roles.values():
            for phrase in [role.title, role.id.replace("-", " "), *role.aliases]:
                self._role_aliases[self._canon(phrase)] = role.id

    @staticmethod
    def _role_text(catalog: Catalog, role_id: str) -> str:
        role = catalog.roles[role_id]
        parts = [role.title, role.title, role.family, *role.aliases]
        for skill_id, importance in sorted(role.skills.items(), key=lambda kv: -kv[1]):
            skill = catalog.skills.get(skill_id)
            if skill:
                parts.extend([skill.name] * (1 + int(round(importance * 2))))
                parts.extend(skill.aliases[:2])
        return " ".join(parts).lower()

    @staticmethod
    def _canon(text: str) -> str:
        return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9+# ]+", " ", text.lower())).strip()

    # -- projection ---------------------------------------------------------

    def encode(self, text: str) -> np.ndarray:
        """Project arbitrary text into the latent space as a unit vector.

        Returns a zero vector only when the text shares nothing at all with
        the corpus — callers treat that as "no signal" rather than as a
        similarity of zero to everything.
        """
        sparse = self.vectorizer.transform([text.lower()])
        if sparse.nnz == 0:
            return np.zeros(self.n_components)
        return _normalise_rows(self.svd.transform(sparse))[0]

    @staticmethod
    def is_empty(vector: np.ndarray) -> bool:
        return not np.any(vector)

    def similar_items(self, vector: np.ndarray) -> np.ndarray:
        """Cosine similarity of a query vector against every catalog item."""
        if self.is_empty(vector):
            return np.zeros(len(self.catalog.item_ids))
        return self.item_vectors @ vector

    def similar_skills(self, vector: np.ndarray) -> np.ndarray:
        if self.is_empty(vector):
            return np.zeros(len(self.catalog.skill_ids))
        return self.skill_vectors @ vector

    # -- goal understanding -------------------------------------------------

    def rank_roles(self, text: str, top_k: int = 3) -> list[tuple[str, float]]:
        """Rank career roles against free text, best first.

        Two signals are blended. The direct cosine between the goal text and
        the role document captures how the role is *named*; the cosine between
        the skills the text implies and the role's target skill vector captures
        what the learner actually described wanting to do. Blending them stops
        a stray word ("...breaking into systems") from dragging the answer to a
        role that merely shares vocabulary.

        An exact alias hit short-circuits both and pins the score to 1.0.
        """
        canon = self._canon(text)
        best_alias, best_len = None, 0
        for alias, role_id in self._role_aliases.items():
            if alias and alias in canon and len(alias) > best_len:
                best_alias, best_len = role_id, len(alias)
        if best_alias:
            # An exact hit is unambiguous: return it alone rather than padding
            # the list with zero-scored roles a disambiguation UI would show.
            return [(best_alias, 1.0)]

        vector = self.encode(text)
        if self.is_empty(vector):
            return []

        text_scores = self.role_vectors @ vector

        # Cosine in skill space between implied skills and each role's target.
        implied = self.match_skills(text)
        skill_scores = np.zeros(len(self.role_ids))
        if implied:
            index = self.catalog.skill_index
            query = np.zeros(len(index))
            for skill_id, weight in implied.items():
                query[index[skill_id]] = weight
            query_norm = np.linalg.norm(query)
            if query_norm > 0:
                for i, role_id in enumerate(self.role_ids):
                    role = self.catalog.roles[role_id]
                    target = np.zeros(len(index))
                    for skill_id, importance in role.skills.items():
                        target[index[skill_id]] = importance
                    target_norm = np.linalg.norm(target)
                    if target_norm > 0:
                        skill_scores[i] = float(query @ target / (query_norm * target_norm))

        blended = 0.45 * text_scores + 0.55 * skill_scores
        order = np.argsort(-blended)[:top_k]
        return [(self.role_ids[i], float(blended[i])) for i in order]

    def match_role(self, text: str) -> tuple[str | None, float]:
        """Best-matching role, or (None, score) when nothing clears the bar.

        A None result is not a failure — the conversation layer turns it into
        a clarifying question rather than guessing at the learner's intent.
        """
        ranked = self.rank_roles(text, top_k=1)
        if not ranked:
            return None, 0.0
        role_id, score = ranked[0]
        if score < ROLE_MATCH_THRESHOLD:
            return None, score
        return role_id, score

    def match_skills(self, text: str, top_k: int = 10) -> dict[str, float]:
        """Extract the skills a free-text goal implies, with confidence weights.

        Returns skill_id -> weight in (0, 1]. Explicit mentions are pinned to
        1.0; inferred skills carry their cosine score, so the gap engine
        naturally trusts what the learner actually said over what we guessed.
        """
        canon = self._canon(text)
        found: dict[str, float] = {}
        for alias, skill_id in self._skill_aliases.items():
            if alias and re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", canon):
                found[skill_id] = 1.0

        vector = self.encode(text)
        if not self.is_empty(vector):
            scores = self.similar_skills(vector)
            order = np.argsort(-scores)[:top_k]
            ceiling = float(scores[order[0]]) if len(order) else 0.0
            floor = max(SKILL_MATCH_THRESHOLD, ceiling * SKILL_RELATIVE_CUTOFF)
            for idx in order:
                score = float(scores[idx])
                if score < floor:
                    break
                found.setdefault(self.catalog.skill_ids[idx], round(score, 4))

        return dict(sorted(found.items(), key=lambda kv: -kv[1]))


SPACE = SemanticSpace()
