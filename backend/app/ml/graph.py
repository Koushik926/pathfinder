"""Prerequisite graph operations.

The catalog's prerequisite edges form a DAG, enforced at build time. This is
the only module that reasons about ordering, so the planner never has to
think about graph mechanics.
"""

from __future__ import annotations

from collections import deque

from app.store import CATALOG, Catalog


def prerequisite_closure(
    item_ids: set[str], catalog: Catalog = CATALOG, known: set[str] | None = None
) -> set[str]:
    """Every item that must be completed before the given items, transitively.

    ``known`` items are treated as already satisfied and are not expanded — a
    learner who has finished Python fundamentals should not have its
    prerequisites dragged back into their path.
    """
    known = known or set()
    needed: set[str] = set()
    queue = deque(item_ids)
    while queue:
        current = queue.popleft()
        item = catalog.items.get(current)
        if item is None:
            continue
        for prereq in item.prereqs:
            if prereq in known or prereq in needed:
                continue
            needed.add(prereq)
            queue.append(prereq)
    return needed


def topological_order(
    item_ids: set[str], priority: dict[str, float] | None = None, catalog: Catalog = CATALOG
) -> list[str]:
    """Order items so every prerequisite precedes its dependents.

    Kahn's algorithm over the induced subgraph. Ties are broken by ``priority``
    (higher first), then prerequisite depth, then id — so output is
    deterministic and the most valuable ready item surfaces first.

    Raises ValueError if the induced subgraph contains a cycle, which would
    mean the catalog invariant was violated after the build.
    """
    priority = priority or {}
    subset = {i for i in item_ids if i in catalog.items}

    indegree = {item_id: 0 for item_id in subset}
    outgoing: dict[str, list[str]] = {item_id: [] for item_id in subset}
    for item_id in subset:
        for prereq in catalog.items[item_id].prereqs:
            if prereq in subset:
                indegree[item_id] += 1
                outgoing[prereq].append(item_id)

    def sort_key(item_id: str) -> tuple:
        item = catalog.items[item_id]
        return (-priority.get(item_id, 0.0), item.depth, item_id)

    ready = sorted([i for i, deg in indegree.items() if deg == 0], key=sort_key)
    ordered: list[str] = []
    while ready:
        current = ready.pop(0)
        ordered.append(current)
        for dependent in outgoing[current]:
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                ready.append(dependent)
        ready.sort(key=sort_key)

    if len(ordered) != len(subset):
        stuck = sorted(subset - set(ordered))
        raise ValueError(f"prerequisite cycle among: {stuck}")
    return ordered


def is_ready(item_id: str, completed: set[str], catalog: Catalog = CATALOG) -> bool:
    """True when every prerequisite of the item has been completed."""
    item = catalog.items.get(item_id)
    if item is None:
        return False
    return all(prereq in completed for prereq in item.prereqs)


def missing_prerequisites(
    item_id: str, completed: set[str], catalog: Catalog = CATALOG
) -> list[str]:
    item = catalog.items.get(item_id)
    if item is None:
        return []
    return [p for p in item.prereqs if p not in completed]


def unlocked_by(item_id: str, completed: set[str], catalog: Catalog = CATALOG) -> list[str]:
    """Items that become newly available once this item is completed."""
    after = completed | {item_id}
    return [
        dependent
        for dependent in catalog.dependents.get(item_id, [])
        if dependent not in completed and is_ready(dependent, after, catalog)
    ]
