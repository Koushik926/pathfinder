"""Compile the Python seed modules into the JSON artefacts the app loads.

Run with:  python -m app.seed.build

Produces, in ``app/data/``:
  skills.json        the taxonomy, with category and aliases
  catalog.json       238 items (courses, projects, assessments) with a
                     validated prerequisite DAG and computed graph depth
  roles.json         career target skill vectors
  interactions.json  a synthetic learner x item co-occurrence matrix used to
                     fit the item-item collaborative-filtering component

The synthetic interactions are generated from a fixed seed so the shipped
model is reproducible: judges running the build get byte-identical output.
"""

from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path

from app.seed import catalog_ai, catalog_apps, catalog_core, catalog_extra
from app.seed.roles import ROLES
from app.seed.skills import SKILLS

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CATALOG_MODULES = (catalog_core, catalog_ai, catalog_apps, catalog_extra)

MODALITIES = {"video", "interactive", "reading", "project", "mixed"}
KINDS = {"course", "project", "assessment"}


def parse_catalog() -> list[dict]:
    """Parse the pipe-delimited seed rows into item dicts."""
    items: list[dict] = []
    for module in CATALOG_MODULES:
        for line in module.ROWS.strip().splitlines():
            if not line.strip():
                continue
            fields = [f.strip() for f in line.split("|")]
            if len(fields) != 11:
                raise ValueError(f"expected 11 fields, got {len(fields)}: {fields[0]}")
            item_id, title, provider, kind, level, hours, modality, skills, prereqs, rating, learners = fields

            if kind not in KINDS:
                raise ValueError(f"{item_id}: unknown kind {kind!r}")
            if modality not in MODALITIES:
                raise ValueError(f"{item_id}: unknown modality {modality!r}")

            skill_weights = {}
            for pair in skills.split(","):
                if not pair.strip():
                    continue
                sid, _, weight = pair.partition(":")
                skill_weights[sid.strip()] = float(weight)

            items.append({
                "id": item_id,
                "title": title,
                "provider": provider,
                "kind": kind,
                "level": int(level),
                "hours": int(hours),
                "modality": modality,
                "skills": skill_weights,
                "prereqs": [p.strip() for p in prereqs.split(",") if p.strip()],
                "rating": float(rating),
                "learners": int(learners),
            })
    return items


def validate(items: list[dict], skill_ids: set[str]) -> None:
    """Fail loudly on the integrity errors that would silently break ranking."""
    ids = [i["id"] for i in items]
    if len(ids) != len(set(ids)):
        dupes = {i for i in ids if ids.count(i) > 1}
        raise ValueError(f"duplicate item ids: {sorted(dupes)}")

    known = set(ids)
    for item in items:
        unknown_skills = set(item["skills"]) - skill_ids
        if unknown_skills:
            raise ValueError(f"{item['id']}: unknown skills {sorted(unknown_skills)}")
        missing = [p for p in item["prereqs"] if p not in known]
        if missing:
            raise ValueError(f"{item['id']}: prerequisites not in catalog: {missing}")
        if item["id"] in item["prereqs"]:
            raise ValueError(f"{item['id']}: item is its own prerequisite")

    uncovered = skill_ids - {s for i in items for s in i["skills"]}
    if uncovered:
        raise ValueError(f"skills with no item teaching them: {sorted(uncovered)}")


def compute_depth(items: list[dict]) -> dict[str, int]:
    """Longest-path depth in the prerequisite DAG; also proves acyclicity.

    Depth 0 means "no prerequisites" — a valid entry point for a beginner.
    A cycle would make a learning path impossible to order, so we detect it
    here rather than at request time.
    """
    by_id = {i["id"]: i for i in items}
    depth: dict[str, int] = {}
    visiting: set[str] = set()

    def walk(item_id: str, trail: list[str]) -> int:
        if item_id in depth:
            return depth[item_id]
        if item_id in visiting:
            cycle = " -> ".join(trail + [item_id])
            raise ValueError(f"prerequisite cycle detected: {cycle}")
        visiting.add(item_id)
        prereqs = by_id[item_id]["prereqs"]
        result = 0 if not prereqs else 1 + max(walk(p, trail + [item_id]) for p in prereqs)
        visiting.discard(item_id)
        depth[item_id] = result
        return result

    for item in items:
        walk(item["id"], [])
    return depth


def synthesise_interactions(items: list[dict], roles: list[dict], seed: int = 20260826) -> dict:
    """Generate a reproducible synthetic enrolment log.

    Real platforms fit collaborative filtering on enrolment history, which we
    do not have. We simulate it: each synthetic learner adopts a role, then
    completes items that serve that role's skills, biased by item popularity
    and with some off-track exploration. The resulting co-occurrence signal is
    what the item-item CF component learns from — it captures "learners who
    took X also took Y" without any real user data.
    """
    rng = random.Random(seed)
    by_id = {i["id"]: i for i in items}
    n_learners = 4000

    # Which items serve each role, scored by how well they cover role skills.
    role_items: dict[str, list[tuple[str, float]]] = {}
    for role in roles:
        scored = []
        for item in items:
            overlap = sum(
                weight * role["skills"].get(sid, 0.0)
                for sid, weight in item["skills"].items()
            )
            if overlap > 0.05:
                scored.append((item["id"], overlap))
        scored.sort(key=lambda pair: -pair[1])
        role_items[role["id"]] = scored[:60]

    sessions: list[list[str]] = []
    for _ in range(n_learners):
        role = rng.choice(roles)
        pool = role_items[role["id"]]
        if not pool:
            continue
        take = rng.randint(4, 14)
        weights = [
            score * (0.4 + by_id[item_id]["learners"] / 2_000_000)
            for item_id, score in pool
        ]
        chosen: set[str] = set()
        for _ in range(take):
            pick = rng.choices(pool, weights=weights, k=1)[0][0]
            chosen.add(pick)
            # Completing an item implies its prerequisites were completed.
            chosen.update(by_id[pick]["prereqs"])
        # A fifth of learners explore outside their track.
        if rng.random() < 0.2:
            chosen.add(rng.choice(items)["id"])
        sessions.append(sorted(chosen))

    co_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    item_counts: dict[str, int] = defaultdict(int)
    for session in sessions:
        for item_id in session:
            item_counts[item_id] += 1
        for a_idx, a in enumerate(session):
            for b in session[a_idx + 1:]:
                co_counts[a][b] += 1
                co_counts[b][a] += 1

    return {
        "seed": seed,
        "n_sessions": len(sessions),
        "item_counts": dict(item_counts),
        "co_counts": {a: dict(b) for a, b in co_counts.items()},
    }


def main() -> None:
    skills = [
        {"id": sid, "name": name, "category": category, "aliases": aliases}
        for sid, name, category, aliases in SKILLS
    ]
    skill_ids = {s["id"] for s in skills}

    roles = [
        {"id": rid, "title": title, "family": family, "aliases": aliases, "skills": skill_map}
        for rid, title, family, aliases, skill_map in ROLES
    ]

    items = parse_catalog()
    validate(items, skill_ids)

    depth = compute_depth(items)
    for item in items:
        item["depth"] = depth[item["id"]]

    interactions = synthesise_interactions(items, roles)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name, payload in (
        ("skills.json", skills),
        ("catalog.json", items),
        ("roles.json", roles),
        ("interactions.json", interactions),
    ):
        path = DATA_DIR / name
        path.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
        print(f"  wrote {name:20s} {path.stat().st_size / 1024:7.1f} KB")

    kinds = defaultdict(int)
    for item in items:
        kinds[item["kind"]] += 1
    print(f"\n  {len(items)} items {dict(kinds)}")
    print(f"  {len(skills)} skills, {len(roles)} roles")
    print(f"  prerequisite DAG: max depth {max(depth.values())}, acyclic ✓")
    print(f"  interactions: {interactions['n_sessions']} synthetic sessions")


if __name__ == "__main__":
    main()
