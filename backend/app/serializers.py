"""Convert internal dataclasses into the JSON shapes the frontend consumes."""

from __future__ import annotations

from app.ml.explain import explain_path
from app.ml.planner import LearningPath
from app.ml.profiler import LearnerProfile
from app.store import CATALOG, Catalog


def profile_to_dict(profile: LearnerProfile, catalog: Catalog = CATALOG) -> dict:
    role = catalog.roles.get(profile.role_id) if profile.role_id else None
    return {
        "id": profile.id,
        "name": profile.name,
        "goal_text": profile.goal_text,
        "role_id": profile.role_id,
        "role_title": role.title if role else None,
        "experience_level": profile.experience_level,
        "hours_per_week": profile.hours_per_week,
        "preferred_modalities": profile.preferred_modalities,
        "interests": profile.interests,
        "completed": [
            {
                "item_id": c.item_id,
                "title": catalog.items[c.item_id].title if c.item_id in catalog.items else c.item_id,
                "months_ago": c.months_ago,
                "score": c.score,
            }
            for c in profile.completed
        ],
        "declared_skills": profile.declared_skills,
        "goal_skills": profile.goal_skills,
    }


def path_to_dict(path: LearningPath, catalog: Catalog = CATALOG) -> dict:
    return {
        "profile_id": path.profile_id,
        "goal_text": path.goal_text,
        "role_id": path.role_id,
        "role_title": path.role_title,
        "total_hours": path.total_hours,
        "total_weeks": path.total_weeks,
        "coverage": path.coverage,
        "gap_count": path.gap_count,
        "readiness_before": path.readiness_before,
        "readiness_after": path.readiness_after,
        "generated_on": path.generated_on,
        "gap_summary": path.gap_summary,
        "narrative": explain_path(path, catalog),
        "milestones": [
            {
                "index": milestone.index,
                "title": milestone.title,
                "focus_skills": [
                    {"id": s, "name": catalog.skill_name(s)} for s in milestone.focus_skills
                ],
                "hours": milestone.hours,
                "weeks": milestone.weeks,
                "starts_on": milestone.starts_on,
                "ends_on": milestone.ends_on,
                "items": [item_to_dict(item, catalog) for item in milestone.items],
            }
            for milestone in path.milestones
        ],
    }


def item_to_dict(item, catalog: Catalog = CATALOG) -> dict:
    return {
        "item_id": item.item_id,
        "title": item.title,
        "kind": item.kind,
        "provider": item.provider,
        "hours": item.hours,
        "level": item.level,
        "modality": item.modality,
        "rating": item.rating,
        "is_prerequisite_fill": item.is_prerequisite_fill,
        "prereqs": [
            {"item_id": p, "title": catalog.items[p].title}
            for p in item.prereqs if p in catalog.items
        ],
        "skills": [
            {"id": s, "name": catalog.skill_name(s), "weight": round(w, 3)}
            for s, w in sorted(item.skills.items(), key=lambda kv: -kv[1])
        ],
        "reason_components": item.reason_components,
        "covers": [
            {"id": s, "name": catalog.skill_name(s), "gap_closed": round(v, 4)}
            for s, v in sorted(item.covers.items(), key=lambda kv: -kv[1])
        ],
    }


def catalog_item_to_dict(item_id: str, catalog: Catalog = CATALOG) -> dict:
    item = catalog.items[item_id]
    return {
        "item_id": item.id,
        "title": item.title,
        "provider": item.provider,
        "kind": item.kind,
        "level": item.level,
        "hours": item.hours,
        "modality": item.modality,
        "rating": item.rating,
        "learners": item.learners,
        "depth": item.depth,
        "skills": [
            {"id": s, "name": catalog.skill_name(s), "weight": round(w, 3)}
            for s, w in sorted(item.skills.items(), key=lambda kv: -kv[1])
        ],
        "prereqs": [
            {"item_id": p, "title": catalog.items[p].title} for p in item.prereqs
        ],
    }
