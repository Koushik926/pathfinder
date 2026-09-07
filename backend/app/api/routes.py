"""HTTP API.

The route layer is deliberately thin: it validates input, calls the ML
engines, and serialises the result. All reasoning lives in ``app.ml``.
"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.llm import LLM
from app.ml import conversation, feedback as feedback_engine
from app.ml.embeddings import SPACE
from app.ml.explain import explain_item
from app.ml.gap import analyse_gaps, gap_vector, readiness
from app.ml.graph import unlocked_by
from app.ml.planner import generate_path
from app.ml.profiler import Completion, compute_mastery, implied_level
from app.ml.recommender import RECOMMENDER
from app.schemas import (
    ChatIn, ChatOut, FeedbackIn, FeedbackOut, ProfileIn, SessionOut,
)
from app.serializers import catalog_item_to_dict, path_to_dict, profile_to_dict
from app.sessions import STORE
from app.store import CATALOG
from app import taxonomy

router = APIRouter(prefix="/api")


def _session_or_404(session_id: str):
    session = STORE.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
    return session


def _refresh_path(session) -> dict:
    """Regenerate the path from the current profile — the single source of truth."""
    session.path = generate_path(session.profile, start=date.today())
    return path_to_dict(session.path)


# -- meta -------------------------------------------------------------------

@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/meta")
def meta() -> dict:
    kinds: dict[str, int] = {}
    for item in CATALOG.items.values():
        kinds[item.kind] = kinds.get(item.kind, 0) + 1
    return {
        "catalog": {
            "items": len(CATALOG.items),
            "by_kind": kinds,
            "skills": len(CATALOG.skills),
            "roles": len(CATALOG.roles),
            "max_prereq_depth": max(i.depth for i in CATALOG.items.values()),
        },
        "taxonomy": taxonomy.summary(len(CATALOG.skills)),
        "model": {
            "embedding_dims": SPACE.n_components,
            "tfidf_features": SPACE.n_features,
            "explained_variance": round(SPACE.explained_variance, 4),
            "cf_sessions": CATALOG.interactions.get("n_sessions", 0),
        },
        "llm": LLM.status,
        "active_sessions": len(STORE),
    }


@router.get("/roles")
def roles() -> dict:
    return {
        "roles": [
            {
                "id": role.id,
                "title": role.title,
                "family": role.family,
                "skill_count": len(role.skills),
                "top_skills": [
                    CATALOG.skill_name(s)
                    for s, _ in sorted(role.skills.items(), key=lambda kv: -kv[1])[:5]
                ],
            }
            for role in sorted(CATALOG.roles.values(), key=lambda r: (r.family, r.title))
        ]
    }


@router.get("/catalog/search")
def catalog_search(q: str = Query(default="", max_length=200), limit: int = 20) -> dict:
    """Semantic search over the catalog, for the 'what have you done' picker."""
    if not q.strip():
        popular = sorted(CATALOG.items.values(), key=lambda i: -i.learners)[:limit]
        return {"results": [catalog_item_to_dict(i.id) for i in popular]}

    vector = SPACE.encode(q)
    scores = SPACE.similar_items(vector)
    ranked = sorted(
        zip(CATALOG.item_ids, scores), key=lambda pair: -pair[1]
    )[:limit]
    return {
        "results": [
            {**catalog_item_to_dict(item_id), "relevance": round(float(score), 4)}
            for item_id, score in ranked
            if score > 0.05
        ]
    }


# -- session ----------------------------------------------------------------

@router.post("/session", response_model=SessionOut)
def create_session(name: str = "Learner") -> SessionOut:
    session = STORE.create(name=name)
    return SessionOut(
        session_id=session.id,
        profile=profile_to_dict(session.profile),
        llm_enabled=LLM.available,
    )


@router.post("/session/{session_id}/chat", response_model=ChatOut)
def chat(session_id: str, payload: ChatIn) -> ChatOut:
    session = _session_or_404(session_id)
    result = conversation.respond(session, payload.message)
    if result["ready"] and session.path is None:
        _refresh_path(session)
    elif result.get("reschedule"):
        # The learner changed their available hours mid-conversation.
        _refresh_path(session)
    return ChatOut(**result)


@router.get("/session/{session_id}/profile")
def get_profile(session_id: str) -> dict:
    session = _session_or_404(session_id)
    return profile_to_dict(session.profile)


@router.get("/session/{session_id}/history")
def get_history(session_id: str) -> dict:
    """The conversation so far.

    The transcript lives on the server, so reopening a session — a reload, a
    shared link, a different device — restores the conversation instead of
    presenting a learner with an empty box and no memory of what was agreed.
    """
    session = _session_or_404(session_id)
    return {
        "turns": [{"role": t.role, "text": t.text} for t in session.history],
        "ready": session.ready,
        "missing_slots": session.missing_slots,
    }


@router.put("/session/{session_id}/profile")
def update_profile(session_id: str, payload: ProfileIn) -> dict:
    """Direct profile edit — the form-based alternative to the chat flow."""
    session = _session_or_404(session_id)
    profile = session.profile

    for field_name in (
        "name", "goal_text", "experience_level", "hours_per_week",
        "preferred_modalities", "interests", "declared_skills", "goal_skills",
    ):
        value = getattr(payload, field_name)
        if value is not None:
            setattr(profile, field_name, value)

    if payload.role_id is not None:
        if payload.role_id and payload.role_id not in CATALOG.roles:
            raise HTTPException(status_code=400, detail=f"Unknown role '{payload.role_id}'.")
        profile.role_id = payload.role_id or None
        # Mark the goal slot satisfied so the chat flow does not re-ask.
        session.pending_role_options = []

    if payload.completed is not None:
        unknown = [c.item_id for c in payload.completed if c.item_id not in CATALOG.items]
        if unknown:
            raise HTTPException(status_code=400, detail=f"Unknown items: {unknown}")
        profile.completed = [
            Completion(item_id=c.item_id, months_ago=c.months_ago, score=c.score)
            for c in payload.completed
        ]
        session.asked.add("history")

    if payload.experience_level is not None:
        session.asked.add("level")
    if payload.hours_per_week is not None:
        session.asked.add("pace")

    path = _refresh_path(session) if (profile.role_id or profile.goal_skills) else None
    return {"profile": profile_to_dict(profile), "path": path}


# -- path, explanation, dashboard -------------------------------------------

@router.get("/session/{session_id}/path")
def get_path(session_id: str, refresh: bool = False) -> dict:
    session = _session_or_404(session_id)
    if not session.profile.role_id and not session.profile.goal_skills:
        raise HTTPException(
            status_code=409,
            detail="No goal set yet. Chat with the assistant or set a role first.",
        )
    if session.path is None or refresh:
        return _refresh_path(session)
    return path_to_dict(session.path)


@router.get("/session/{session_id}/explain/{item_id}")
def explain(session_id: str, item_id: str) -> dict:
    """Why this item was recommended, from the ranker's own attributions."""
    session = _session_or_404(session_id)
    if item_id not in CATALOG.items:
        raise HTTPException(status_code=404, detail=f"Unknown item '{item_id}'.")

    profile = session.profile
    mastery, confidence = compute_mastery(profile)
    level = implied_level(profile, mastery)
    gaps = gap_vector(analyse_gaps(profile, mastery, confidence))

    scored = RECOMMENDER.recommend(
        profile, gaps, level, k=1, candidates={item_id}, exclude=set()
    )
    if not scored:
        raise HTTPException(
            status_code=409,
            detail="That item is already complete or not scoreable for this profile.",
        )

    # If this item sits in the learner's current path as groundwork, the graph
    # already knows what depends on it — that is the honest answer to "why is
    # this here?", and it is not something the ranker can supply.
    required_for: list[str] = []
    if session.path is not None:
        required_for = next(
            (i.required_for for i in session.path.all_items if i.item_id == item_id), []
        )

    explanation = explain_item(
        scored[0], mastery=mastery, required_for=required_for, profile=profile
    )
    narrated = LLM.narrate(
        explanation.as_text(),
        "Rewrite this recommendation rationale for the learner in a warm, direct voice.",
    )
    return {
        "item_id": explanation.item_id,
        "headline": explanation.headline,
        "reasons": explanation.reasons,
        "narrative": narrated,
        "covers": explanation.covers,
        "prerequisites": explanation.prerequisites,
        "unlocks": explanation.unlocks,
        "required_for": explanation.required_for,
        "evidence": explanation.evidence,
        "source": "claude" if narrated else "template",
    }


@router.get("/session/{session_id}/dashboard")
def dashboard(session_id: str) -> dict:
    """Everything the progress view renders."""
    session = _session_or_404(session_id)
    profile = session.profile
    mastery, confidence = compute_mastery(profile)
    level = implied_level(profile, mastery)
    all_gaps = analyse_gaps(profile, mastery, confidence, include_met=True)
    open_gaps = [g for g in all_gaps if not g.is_met]

    if session.path is None and (profile.role_id or profile.goal_skills):
        _refresh_path(session)

    completed_ids = profile.completed_ids
    path_items = session.path.all_items if session.path else []

    # Progress is (work finished) / (work finished + work remaining). Measuring
    # against the current path alone would always read zero, because the path is
    # regenerated after each completion and excludes what is already done.
    done_ids = [i for i in session.completed_in_path if i in CATALOG.items]
    hours_done = sum(CATALOG.items[i].hours for i in done_ids)
    hours_remaining = sum(i.hours for i in path_items)
    hours_total = hours_done + hours_remaining
    items_total = len(done_ids) + len(path_items)

    # Next actions: ready, not yet done, in path order.
    next_actions = [
        {
            "item_id": item.item_id,
            "title": item.title,
            "kind": item.kind,
            "hours": item.hours,
            "provider": item.provider,
            "unlocks": len(unlocked_by(item.item_id, completed_ids)),
        }
        for item in path_items
        if item.item_id not in completed_ids
        and all(p in completed_ids for p in item.prereqs)
    ][:4]

    by_category: dict[str, dict] = {}
    for gap in all_gaps:
        bucket = by_category.setdefault(
            gap.category, {"category": gap.category, "target": 0.0, "mastery": 0.0, "skills": 0}
        )
        bucket["target"] += gap.target
        bucket["mastery"] += min(gap.mastery, gap.target)
        bucket["skills"] += 1
    for bucket in by_category.values():
        bucket["progress"] = round(bucket["mastery"] / bucket["target"], 4) if bucket["target"] else 0.0
        bucket["target"] = round(bucket["target"], 3)
        bucket["mastery"] = round(bucket["mastery"], 3)

    return {
        "profile": profile_to_dict(profile),
        "readiness": readiness(profile, mastery),
        "implied_level": level,
        "skills": {
            "tracked": len(all_gaps),
            "met": len(all_gaps) - len(open_gaps),
            "open": len(open_gaps),
            "by_category": sorted(by_category.values(), key=lambda b: -b["target"]),
            "top_gaps": [
                {
                    "skill_id": g.skill_id, "name": g.name, "category": g.category,
                    "target": g.target, "mastery": g.mastery, "confidence": g.confidence,
                }
                for g in open_gaps[:8]
            ],
            "strongest": [
                {"skill_id": s, "name": CATALOG.skill_name(s), "mastery": round(v, 3)}
                for s, v in list(mastery.items())[:8]
            ],
        },
        "progress": {
            "items_done": len(done_ids),
            "items_total": items_total,
            "hours_done": hours_done,
            "hours_total": hours_total,
            "percent": round(hours_done / hours_total, 4) if hours_total else 0.0,
        },
        "milestones": [
            {
                "index": m.index,
                "title": m.title,
                "hours": m.hours,
                "ends_on": m.ends_on,
                "done": sum(1 for i in m.items if i.item_id in completed_ids),
                "total": len(m.items),
            }
            for m in (session.path.milestones if session.path else [])
        ],
        "next_actions": next_actions,
    }


@router.post("/session/{session_id}/feedback", response_model=FeedbackOut)
def submit_feedback(session_id: str, payload: FeedbackIn) -> FeedbackOut:
    session = _session_or_404(session_id)
    profile = session.profile

    if payload.kind == "completion":
        if not payload.item_id:
            raise HTTPException(status_code=400, detail="item_id is required for a completion.")
        was_planned = session.path is not None and any(
            item.item_id == payload.item_id for item in session.path.all_items
        )
        result = feedback_engine.apply_completion(profile, payload.item_id, payload.score)
        if result.regenerate and was_planned and payload.item_id not in session.completed_in_path:
            session.completed_in_path.append(payload.item_id)
    elif payload.kind == "reaction":
        if not payload.item_id or not payload.reaction:
            raise HTTPException(status_code=400, detail="item_id and reaction are required.")
        result = feedback_engine.apply_reaction(profile, payload.item_id, payload.reaction)
    else:
        if payload.hours_per_week is None:
            raise HTTPException(status_code=400, detail="hours_per_week is required.")
        result = feedback_engine.apply_pace(profile, payload.hours_per_week)

    path = _refresh_path(session) if result.regenerate else None
    return FeedbackOut(changes=result.changes, regenerated=result.regenerate, path=path)
