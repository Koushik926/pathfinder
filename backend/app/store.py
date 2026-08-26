"""Loads the compiled catalog artefacts and exposes them as typed records.

Everything here is read-only and loaded once at import time. The catalog is
small (238 items) so it lives entirely in memory; there is no database in the
request path, which keeps recommendation latency in the low milliseconds.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"


@dataclass(frozen=True)
class Skill:
    id: str
    name: str
    category: str
    aliases: list[str]


@dataclass(frozen=True)
class Item:
    """A course, project or assessment in the catalog."""

    id: str
    title: str
    provider: str
    kind: str          # course | project | assessment
    level: int         # 1 beginner, 2 intermediate, 3 advanced
    hours: int
    modality: str      # video | interactive | reading | project | mixed
    skills: dict[str, float]
    prereqs: list[str]
    rating: float
    learners: int
    depth: int         # longest-path depth in the prerequisite DAG

    @property
    def is_graded(self) -> bool:
        return self.kind in ("project", "assessment")


@dataclass(frozen=True)
class Role:
    id: str
    title: str
    family: str
    aliases: list[str]
    skills: dict[str, float]


@dataclass
class Catalog:
    skills: dict[str, Skill]
    items: dict[str, Item]
    roles: dict[str, Role]
    interactions: dict = field(repr=False, default_factory=dict)

    @cached_property
    def item_ids(self) -> list[str]:
        """Stable ordering — every matrix in the ML layer indexes by this."""
        return sorted(self.items)

    @cached_property
    def skill_ids(self) -> list[str]:
        return sorted(self.skills)

    @cached_property
    def item_index(self) -> dict[str, int]:
        return {item_id: i for i, item_id in enumerate(self.item_ids)}

    @cached_property
    def skill_index(self) -> dict[str, int]:
        return {skill_id: i for i, skill_id in enumerate(self.skill_ids)}

    @cached_property
    def dependents(self) -> dict[str, list[str]]:
        """Reverse prerequisite edges: item -> items that require it."""
        out: dict[str, list[str]] = {item_id: [] for item_id in self.items}
        for item in self.items.values():
            for prereq in item.prereqs:
                out[prereq].append(item.id)
        return out

    def skill_name(self, skill_id: str) -> str:
        skill = self.skills.get(skill_id)
        return skill.name if skill else skill_id

    def item_text(self, item: Item) -> str:
        """The document used to build the item's semantic embedding.

        Skill names and categories are folded in (and skill names repeated in
        proportion to how strongly the item teaches them) so that a learner
        goal phrased in skill terms — "I want to learn about attention" —
        lands near the right items even when the title never says so.
        """
        parts = [item.title, item.title, item.provider, item.kind, item.modality]
        for skill_id, weight in sorted(item.skills.items(), key=lambda kv: -kv[1]):
            skill = self.skills.get(skill_id)
            if not skill:
                continue
            repeats = 1 + int(round(weight * 3))
            parts.extend([skill.name] * repeats)
            parts.append(skill.category)
            parts.extend(skill.aliases[:3])
        return " ".join(parts).lower()

    def skill_text(self, skill: Skill) -> str:
        return " ".join([skill.name, skill.name, skill.category, *skill.aliases]).lower()


def _read(name: str):
    path = DATA_DIR / name
    if not path.exists():
        raise FileNotFoundError(
            f"{path} is missing. Build the catalog first:  python -m app.seed.build"
        )
    return json.loads(path.read_text())


def load_catalog() -> Catalog:
    skills = {s["id"]: Skill(**s) for s in _read("skills.json")}
    items = {i["id"]: Item(**i) for i in _read("catalog.json")}
    roles = {r["id"]: Role(**r) for r in _read("roles.json")}
    interactions = _read("interactions.json")
    return Catalog(skills=skills, items=items, roles=roles, interactions=interactions)


CATALOG = load_catalog()
