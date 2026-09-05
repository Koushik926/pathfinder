"""The conversational front door.

A learner describes a goal in their own words; this module turns that into a
complete ``LearnerProfile`` and keeps talking to them afterwards.

It is a slot-filling dialogue rather than an open-ended chat, for a reason a
demo makes obvious: to plan a path we need five specific things (goal, level,
history, pace, format). A state machine asks for exactly what is still missing
and stops asking the moment it has enough. Every slot can also be filled out
of order from a single sentence — "I'm a second-year who knows Python and can
do 10 hours a week, I want to be an ML engineer" fills four slots at once.

Claude, when configured, improves slot extraction and rewrites the replies.
Neither is required: the regex and embedding parsers below fill the same slots
and the templates below produce the same information in plainer words.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from app.llm import LLM
from app.ml import qa
from app.ml.embeddings import SPACE
from app.ml.profiler import Completion, LearnerProfile
from app.store import CATALOG, Catalog

# Ordered most-specific first. These must recognise the exact wording of the
# quick-reply buttons the UI offers, otherwise clicking a button says nothing.
LEVEL_PATTERNS = [
    (3, r"\b(advanced|expert|senior|experienced|several years|many years|professional|work in it)\b"),
    (2, r"\b(intermediate|some grounding|some experience|a bit of experience|familiar|comfortable|worked with|course or two|1 year|two years|2 years)\b"),
    (1, r"\b(beginner|just starting|complete beginner|new to|starting out|no experience|fresher|first year|never|from scratch)\b"),
]

# Suffixes are matched explicitly: a bare \bvideo\b misses "videos", and
# \bwatch\b misses "watching", which is how learners actually phrase this.
_S = r"(?:s|es)?"
_ING = r"(?:ing|es|ed|s)?"
MODALITY_PATTERNS = {
    "video": rf"\b(?:video{_S}|lecture{_S}|watch{_ING}|youtube)\b",
    "interactive": rf"\b(?:interactive|hands.?on|practic{_ING}|practice{_S}|exercise{_S}|coding along)\b",
    "reading": rf"\b(?:read{_ING}|book{_S}|article{_S}|docs|documentation)\b",
    "project": rf"\b(?:project{_S}|build{_ING}|portfolio{_S})\b",
}

# Below this, a top-ranked role is too weak to commit to on the learner's
# behalf. Character n-grams make the matcher robust to unseen word forms, but
# they also mean nonsense scores non-zero: "zxcv" reaches "cv" reaches Computer
# Vision. Committing at that confidence invents a career for someone who typed
# noise, so we show real choices instead.
COMMIT_THRESHOLD = 0.40

# Offered when we genuinely cannot read the goal. Breadth over precision:
# these span the families most learners arrive wanting.
FALLBACK_ROLES = [
    "sde-placement", "data-scientist", "genai-engineer",
    "fullstack-dev", "devops-engineer",
]

ASK = {
    "goal": "What do you want to be able to do? Describe it however feels natural — a job title, a project you want to build, or just a topic you're curious about.",
    "level": "How much ground have you already covered in this area?",
    "history": "Which of these have you already done? Pick any that apply, or tell me in your own words — and say 'none' if you're starting fresh.",
    "pace": "Roughly how many hours a week can you give this?",
}


@dataclass
class Turn:
    role: str      # "learner" | "assistant"
    text: str


@dataclass
class Session:
    """One learner's conversation and the profile being assembled from it."""

    id: str
    profile: LearnerProfile
    history: list[Turn] = field(default_factory=list)
    asked: set[str] = field(default_factory=set)
    pending_role_options: list[str] = field(default_factory=list)
    role_prompts: int = 0
    last_asked: str = ""
    path: Any = None
    # Items completed while following the path, in the order they were done.
    # The path itself cannot record this: it regenerates after every completion
    # and excludes finished work by construction, so progress measured against
    # the current path alone is permanently zero.
    completed_in_path: list[str] = field(default_factory=list)

    @property
    def missing_slots(self) -> list[str]:
        missing = []
        if not self.profile.role_id and not self.profile.goal_skills:
            missing.append("goal")
        if "level" not in self.asked:
            missing.append("level")
        if "history" not in self.asked:
            missing.append("history")
        if "pace" not in self.asked:
            missing.append("pace")
        return missing

    @property
    def ready(self) -> bool:
        return not self.missing_slots


def _extract_level(text: str) -> int | None:
    lowered = text.lower()
    for level, pattern in LEVEL_PATTERNS:
        if re.search(pattern, lowered):
            return level
    return None


def _extract_hours(text: str) -> float | None:
    lowered = text.lower()
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:hours?|hrs?|h)\b", lowered)
    if match:
        return float(match.group(1))
    match = re.search(r"\b(\d+(?:\.\d+)?)\s*(?:per|a|each)\s*week\b", lowered)
    if match:
        return float(match.group(1))
    return None


def _extract_modalities(text: str) -> list[str]:
    lowered = text.lower()
    return [name for name, pattern in MODALITY_PATTERNS.items() if re.search(pattern, lowered)]


# Words too common in course titles to identify anything on their own.
_TITLE_STOPWORDS = {
    "the", "a", "an", "to", "for", "of", "in", "with", "and", "or", "on",
    "your", "you", "from", "by", "at", "course", "intro", "introduction",
    "fundamentals", "essentials", "basics", "complete", "guide", "practice",
    "practical", "modern", "advanced", "beginner", "part", "i", "ii",
}


# Phrases that mark a message as a claim about the past rather than a goal.
_COMPLETION_CUE = re.compile(
    r"\b(did|done|completed|finished|took|taken|studied|covered|"
    r"went through|already|know|knew|learnt|learned|familiar with)\b"
)


def _match_known_items(
    text: str, catalog: Catalog, threshold: float = 0.7, require_cue: bool = True
) -> list[str]:
    """Find catalog items the learner says they have already completed.

    Substring matching is too brittle here — a learner writes "Python for
    Everybody", not "Python for Everybody: Getting Started". Instead we ask
    what fraction of an item's *distinctive* title words appear in the
    message, which tolerates the subtitle being dropped or reworded.
    """
    lowered = text.lower()
    # Without this gate, "I want to become a machine learning engineer" matches
    # the course "Intro to Machine Learning" and is silently recorded as
    # completed — turning the learner's goal into their history. A title match
    # only counts when the sentence is actually claiming past work. The gate is
    # lifted when we have just asked what they have completed, since the reply
    # is then a bare list of titles.
    if require_cue and not _COMPLETION_CUE.search(lowered):
        return []

    words = set(re.findall(r"[a-z0-9+#.]+", lowered))
    if not words:
        return []

    hits: list[str] = []
    for item in catalog.items.values():
        title = re.sub(r"^(project|assessment):\s*", "", item.title.lower())
        # Drop a trailing subtitle, which learners routinely omit.
        title = title.split(":")[0]
        tokens = {
            w for w in re.findall(r"[a-z0-9+#.]+", title)
            if w not in _TITLE_STOPWORDS and len(w) > 1
        }
        if len(tokens) < 2:
            continue
        overlap = len(tokens & words) / len(tokens)
        if overlap >= threshold:
            hits.append(item.id)
    return hits


def _apply_extraction(
    session: Session, text: str, catalog: Catalog, answering_prompt: bool = False
) -> list[str]:
    """Fill whatever slots this message provides. Returns slot names filled.

    ``answering_prompt`` marks the message as a reply to a question we just
    asked (experience, history, pace, or a role disambiguation). Such a reply
    must never be mined for goal intent: "nothing" and "6 hours a week" both
    return plausible-looking skills from the embedding tail — algorithms,
    GraphQL, React — and accumulating those turned an "I want to learn AI"
    request into a JavaScript path.
    """
    profile = session.profile
    filled: list[str] = []

    # Claude first, when available — it reads intent better than regexes.
    parsed = LLM.parse_goal(text) if LLM.available else None

    level = None
    hours = None
    if parsed:
        if parsed.experience_level != "unknown":
            level = {"beginner": 1, "intermediate": 2, "advanced": 3}[parsed.experience_level]
        if parsed.hours_per_week > 0:
            hours = float(parsed.hours_per_week)
        # Claude's skill names are resolved against the real taxonomy; anything
        # that does not resolve is discarded rather than trusted.
        for name in parsed.skills:
            for skill_id, weight in SPACE.match_skills(name, top_k=2).items():
                if weight >= 0.5:
                    profile.goal_skills[skill_id] = max(profile.goal_skills.get(skill_id, 0.0), weight)
        for name in parsed.known_topics:
            for skill_id, weight in SPACE.match_skills(name, top_k=2).items():
                if weight >= 0.5:
                    profile.declared_skills[skill_id] = max(profile.declared_skills.get(skill_id, 0.0), 0.6)
        if parsed.known_topics:
            filled.append("history")
            session.asked.add("history")

    level = level if level is not None else _extract_level(text)
    hours = hours if hours is not None else _extract_hours(text)

    if level is not None:
        profile.experience_level = level
        session.asked.add("level")
        filled.append("level")

    if hours is not None:
        profile.hours_per_week = max(1.0, min(60.0, hours))
        session.asked.add("pace")
        filled.append("pace")

    # Interests: topics the learner names for themselves, as distinct from the
    # skills their chosen role happens to require. Recorded whenever they are
    # named explicitly (an alias hit, not a weak embedding neighbour), so the
    # profile reflects what this person is drawn to and not just the job title.
    if not answering_prompt:
        for skill_id, weight in SPACE.match_skills(text).items():
            if weight >= 1.0:
                name = catalog.skill_name(skill_id)
                if name not in profile.interests:
                    profile.interests.append(name)
                    if "interests" not in filled:
                        filled.append("interests")

    modalities = _extract_modalities(text)
    if modalities:
        profile.preferred_modalities = modalities
        filled.append("format")

    completed = _match_known_items(
        text, catalog, require_cue=(session.last_asked != "history")
    )
    if completed:
        existing = profile.completed_ids
        for item_id in completed:
            if item_id not in existing:
                profile.completed.append(Completion(item_id=item_id, months_ago=6.0))
        session.asked.add("history")
        filled.append("history")

    if re.search(r"\b(nothing|none|from scratch|no experience|starting fresh|absolute beginner)\b", text.lower()):
        session.asked.add("history")
        filled.append("history")

    # Goal resolution, if the goal slot is still open and this message is
    # actually a statement of intent rather than an answer to a prompt.
    if not profile.role_id and not answering_prompt:
        goal_source = text
        if parsed and parsed.role_hint:
            goal_source = parsed.role_hint
        ranked = SPACE.rank_roles(goal_source, top_k=3)
        skills = SPACE.match_skills(text)

        if ranked and ranked[0][1] >= 0.55:
            profile.role_id = ranked[0][0]
            profile.goal_text = profile.goal_text or text
            session.pending_role_options = []
            filled.append("goal")
        elif ranked and ranked[0][1] >= 0.30:
            # Plausible but not certain — ask rather than guess.
            session.pending_role_options = [rid for rid, _ in ranked]
            profile.goal_text = profile.goal_text or text
        else:
            # No role matched. Fall back to skills only when the learner clearly
            # named them — an explicit alias hit (1.0) or a strong match. The
            # weak tail of the embedding is noise, not intent.
            confident = {k: v for k, v in skills.items() if v >= 0.75}
            if confident:
                profile.goal_skills.update(confident)
                profile.goal_text = profile.goal_text or text
                filled.append("goal")

    return filled


def _history_suggestions(session: Session, catalog: Catalog, limit: int = 6) -> list[dict]:
    """Popular entry-level items on the learner's track, to tick off quickly."""
    profile = session.profile
    if not profile.role_id or profile.role_id not in catalog.roles:
        return []
    role = catalog.roles[profile.role_id]
    scored = []
    for item in catalog.items.values():
        if item.kind != "course" or item.id in profile.completed_ids:
            continue
        overlap = sum(w * role.skills.get(s, 0.0) for s, w in item.skills.items())
        if overlap > 0.1:
            scored.append((overlap * (1 + item.learners / 2_000_000), item))
    scored.sort(key=lambda pair: -pair[0])
    return [
        {"item_id": item.id, "title": item.title, "provider": item.provider}
        for _, item in scored[:limit]
    ]


def _level_options() -> list[dict]:
    return [
        {"value": 1, "label": "Just starting", "detail": "New to this area"},
        {"value": 2, "label": "Some grounding", "detail": "I've done a course or two"},
        {"value": 3, "label": "Experienced", "detail": "I work in it already"},
    ]


def respond(session: Session, message: str, catalog: Catalog = CATALOG) -> dict:
    """Process one learner message and produce the assistant's reply."""
    session.history.append(Turn("learner", message))
    # Snapshot before extraction: _apply_extraction may itself update the pace,
    # which would make a later "did the pace change?" comparison always false.
    hours_before = session.profile.hours_per_week

    # Resolve a pending "which of these did you mean" question first.
    was_disambiguating = bool(session.pending_role_options)
    if was_disambiguating:
        chosen = _resolve_role_choice(message, session.pending_role_options, catalog)
        if chosen:
            session.profile.role_id = chosen
            session.pending_role_options = []

    answering_prompt = was_disambiguating or session.last_asked in ("level", "history", "pace")
    filled = _apply_extraction(session, message, catalog, answering_prompt=answering_prompt)

    if session.pending_role_options and session.role_prompts >= 2:
        # Termination is guaranteed by a monotonically increasing counter:
        # two attempts at the ranked options, then one at a broad fallback
        # list, then we commit. Without a hard cap this loops forever on a
        # learner who never picks — which is exactly the deadlock this
        # replaced, only more politely worded.
        ranked = SPACE.rank_roles(session.profile.goal_text or "", top_k=1)
        score = ranked[0][1] if ranked else 0.0
        strong = score >= COMMIT_THRESHOLD

        if strong or session.role_prompts >= 3:
            # A weak-but-real match still beats an arbitrary default, so long as
            # the learner used vocabulary the catalog recognises. With no
            # lexical signal at all the ranking is character-level noise and a
            # neutral, popular default is the honest choice.
            has_words = SPACE.lexical_signal(session.profile.goal_text or "") > 0
            if strong or (has_words and ranked):
                best = session.pending_role_options[0] if strong else ranked[0][0]
            else:
                best = next((r for r in FALLBACK_ROLES if r in catalog.roles),
                            session.pending_role_options[0])
            session.profile.role_id = best
            session.pending_role_options = []
            filled.append("goal")
        else:
            # One honest attempt at a broad, concrete list before committing.
            session.role_prompts += 1
            options = [
                {"value": rid, "label": catalog.roles[rid].title,
                 "detail": catalog.roles[rid].family}
                for rid in FALLBACK_ROLES if rid in catalog.roles
            ]
            session.pending_role_options = [o["value"] for o in options]
            reply = _narrate(
                "I couldn't quite read that one. Rather than guess, here are the "
                "goals people most often start from — pick whichever is closest, "
                "or describe yours again in different words.",
                "Tell the learner you could not understand their goal and ask them "
                "to pick from the list or rephrase. Be encouraging, not apologetic.",
            )
            return _package(session, reply, "choose_role", options=options)

    if session.pending_role_options:
        session.role_prompts += 1
        options = [
            {"value": rid, "label": catalog.roles[rid].title, "detail": catalog.roles[rid].family}
            for rid in session.pending_role_options
        ]
        reply = _narrate(
            "I can read that a few ways. Which is closest to what you're after?",
            f"The learner said: {message!r}. Ask which of these goals they mean: "
            + ", ".join(o["label"] for o in options),
        )
        return _package(session, reply, "choose_role", options=options)

    missing = session.missing_slots
    if not missing:
        # Setup is done. From here the learner is asking about their path, not
        # filling in slots — route to the question answerer rather than
        # repeating the same "that's everything I need" line at every message.
        if session.path is not None:
            # A pace change is an instruction, not a question; apply it here so
            # "I only have 5 hours a week now" reschedules instead of being
            # answered with a description of the old schedule.
            hours = _extract_hours(message)
            if hours and hours != hours_before:
                previous = hours_before
                session.profile.hours_per_week = max(1.0, min(60.0, hours))
                weeks = round(session.path.total_hours / session.profile.hours_per_week, 1)
                reply = _narrate(
                    f"Updated from {previous:g} to {session.profile.hours_per_week:g} hours "
                    f"a week — that puts your path at about {weeks} weeks. "
                    f"Rebuilding the schedule now.",
                    "Tell the learner their weekly hours changed and the schedule is being rebuilt.",
                )
                return _package(session, reply, "pace_changed", reschedule=True)

            result = qa.answer(session.profile, session.path, message, catalog)
            return _package(session, result.text, result.intent, items=result.item_ids)
        return _package(session, _ready_message(session, catalog), "ready")

    slot = missing[0]
    session_ack = _acknowledge(session, filled, catalog)
    question = ASK[slot]
    reply = _narrate(
        f"{session_ack}{question}".strip(),
        f"Acknowledge what the learner just told you, then ask: {question}",
    )

    options: list[dict] = []
    if slot == "level":
        options = _level_options()
    elif slot == "history":
        options = _history_suggestions(session, catalog)

    return _package(session, reply, f"ask_{slot}", options=options)


def _resolve_role_choice(message: str, options: list[str], catalog: Catalog) -> str | None:
    """Work out which offered role the learner picked.

    People answer this in every possible way: the full title, one distinctive
    word from it, a position ("the first one", "1"), or by restating the goal.
    """
    lowered = message.lower()

    for role_id in options:
        role = catalog.roles[role_id]
        if role.title.lower() in lowered or role_id.replace("-", " ") in lowered:
            return role_id

    # A word that distinguishes exactly one of the options on offer. Which
    # words are distinctive depends on the offered set, not on a fixed list:
    # among "Data Analyst / Data Scientist / Data Engineer", "data" separates
    # nothing and "analyst" separates everything.
    said = set(re.findall(r"[a-z]+", lowered))
    title_words = {
        role_id: {w for w in re.findall(r"[a-z]+", catalog.roles[role_id].title.lower()) if len(w) > 3}
        for role_id in options
    }
    for role_id, words in title_words.items():
        shared = set().union(*(w for r, w in title_words.items() if r != role_id)) if len(options) > 1 else set()
        distinctive = words - shared
        if distinctive & said:
            return role_id

    # Ordinals, longest-first: "the second one" contains "one", so a naive
    # scan that checks "one" before "second" selects the wrong option.
    ordinals = [("second", 1), ("third", 2), ("first", 0), ("2nd", 1), ("3rd", 2),
                ("1st", 0), ("three", 2), ("two", 1)]
    for word, index in ordinals:
        if re.search(rf"\b{word}\b", lowered) and index < len(options):
            return options[index]
    match = re.search(r"\b([123])\b", lowered)
    if match:
        index = int(match.group(1)) - 1
        if 0 <= index < len(options):
            return options[index]

    # They may have restated the goal instead of picking; re-rank and accept a
    # clear winner that is one of the options on offer.
    ranked = SPACE.rank_roles(message, top_k=1)
    if ranked and ranked[0][1] >= 0.55 and ranked[0][0] in options:
        return ranked[0][0]
    return None


def _acknowledge(session: Session, filled: list[str], catalog: Catalog) -> str:
    if not filled:
        return ""
    profile = session.profile
    if "goal" in filled:
        if profile.role_id:
            role = catalog.roles[profile.role_id]
            return f"Got it — aiming for {role.title}. "
        if profile.goal_skills:
            names = [catalog.skill_name(s) for s in list(profile.goal_skills)[:2]]
            return f"Got it — focusing on {' and '.join(names)}. "
    if "history" in filled:
        count = len(profile.completed)
        noun = "item" if count == 1 else "items"
        return f"Noted, that's {count} {noun} already behind you. "
    if "level" in filled:
        return "Thanks. "
    if "pace" in filled:
        return f"{profile.hours_per_week:g} hours a week it is. "
    return ""


def _ready_message(session: Session, catalog: Catalog) -> str:
    profile = session.profile
    goal = catalog.roles[profile.role_id].title if profile.role_id else "your goal"
    facts = (
        f"goal={goal}; level={profile.experience_level}/3; "
        f"hours_per_week={profile.hours_per_week:g}; "
        f"already_completed={len(profile.completed)} items"
    )
    template = (
        f"That's everything I need. Building your path to {goal} now — "
        f"{profile.hours_per_week:g} hours a week, starting from where you already are."
    )
    return _narrate(template, f"Tell the learner you have what you need and are building their path. {facts}")


def _narrate(template: str, instruction: str) -> str:
    """Prefer Claude's wording; fall back to the template verbatim."""
    return LLM.narrate(f"Draft reply: {template}", instruction) or template


def _package(
    session: Session,
    reply: str,
    intent: str,
    options: list[dict] | None = None,
    items: list[str] | None = None,
    reschedule: bool = False,
) -> dict:
    session.history.append(Turn("assistant", reply))
    session.last_asked = intent[4:] if intent.startswith("ask_") else ""
    return {
        "reply": reply,
        "intent": intent,
        "options": options or [],
        # Items the answer refers to, so the interface can highlight them.
        "items": items or [],
        "reschedule": reschedule,
        "ready": session.ready,
        "missing_slots": session.missing_slots,
        "profile_preview": {
            "role_id": session.profile.role_id,
            "goal_skills": list(session.profile.goal_skills)[:6],
            "experience_level": session.profile.experience_level,
            "hours_per_week": session.profile.hours_per_week,
            "completed": len(session.profile.completed),
            "modalities": session.profile.preferred_modalities,
        },
        "llm_enabled": LLM.available,
    }
