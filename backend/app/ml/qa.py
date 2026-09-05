"""Answering a learner's questions about the path they were given.

The brief asks for an assistant that explains recommendations *and answers
learner queries*. Slot-filling gets someone a path; it does not help the person
staring at twenty items wondering why Linear Algebra comes before the thing
they actually wanted, or whether they can skip Python, or what happens if they
only have five hours next week.

Every answer here is computed from the same objects that produced the path —
the profile, the gap vector, the prerequisite graph, the schedule. Nothing is
invented, and nothing is asked of a language model that the system already
knows. When Claude is configured it rewrites the computed answer into warmer
prose; without it the wording below is used directly.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.llm import LLM
from app.ml.embeddings import SPACE
from app.ml.gap import analyse_gaps, readiness
from app.ml.graph import missing_prerequisites, unlocked_by
from app.ml.profiler import LearnerProfile, compute_mastery
from app.store import CATALOG, Catalog


@dataclass
class Answer:
    text: str
    intent: str
    item_ids: list[str]


# Ordered: the first pattern that matches wins, so put the specific ones first.
INTENT_PATTERNS = [
    ("ordering",   r"\b(why|how come)\b.*\b(before|after|first|order|early|earlier|later|start with)\b"
                   r"|\border\b.*\bwhy\b|why.*\bthen\b"),
    # "why do I need X" is a request for a reason, not a request to remove it,
    # so the skip patterns must not claim anything starting with "why".
    ("skip",       r"^(?!.*\bwhy\b).*\b(skip|drop|remove|can i avoid|leave out|"
                   r"do i (really )?(need|have to)|don'?t want)\b"),
    ("duration",   r"\b(how long|how many (weeks|months|hours|days)|when will i|finish|complete by|duration|time will)\b"),
    ("faster",     r"\b(faster|quicker|shorter|speed (it )?up|reduce|cut down|less time|too long)\b"),
    ("difficulty", r"\b(too hard|too easy|difficult|hard for me|manageable|struggle|beginner friendly|over my head)\b"),
    ("next",       r"\b(what (should|do) i (do|start)|where (do|should) i (start|begin)|next step|first thing|start with)\b"),
    ("progress",   r"\b(how am i doing|my progress|how far|am i on track|done so far|ready yet)\b"),
    ("skills",     r"\bwhat .{0,20}\b(learn|teach|gain|come out|end up)\b"
                   r"|\b(which|what) skills\b|\bskills (will|do|does)\b|\boutcomes?\b"),
    ("why_item",   r"\b(why (is|are|do i need|this|that)|reason for|purpose of|what.*for)\b"),
    ("overview",   r"\b(what('s| is) (the )?plan|explain (the |my )?(path|plan|roadmap)|summar|overview|walk me through)\b"),
]


def classify(message: str) -> str:
    lowered = message.lower()
    for intent, pattern in INTENT_PATTERNS:
        if re.search(pattern, lowered):
            return intent
    return "general"


def find_items(message: str, path, catalog: Catalog = CATALOG, limit: int = 2) -> list[str]:
    """Which items in the learner's path is this question about?

    Matches on distinctive title words first, then falls back to the skill the
    question is about — "can I skip the Python part" names no course title, but
    it clearly means the Python items.
    """
    lowered = message.lower()
    # "why is X before Y" is a question about X's position. Searching the whole
    # sentence matches Y just as readily, and answering about the wrong item
    # reads as though the assistant misunderstood.
    pivot = re.split(r"\b(?:before|after|ahead of|prior to)\b", lowered, maxsplit=1)
    subject = pivot[0] if len(pivot) > 1 else lowered

    words = set(re.findall(r"[a-z0-9+#.]+", subject))
    if not words:
        return []

    stop = {"the", "a", "an", "to", "for", "of", "in", "with", "and", "or", "on", "i",
            "do", "is", "it", "this", "that", "my", "me", "why", "can", "should", "need",
            "part", "before", "after", "skip", "how", "long", "what", "does", "are"}

    scored: list[tuple[float, str]] = []
    for item in path.all_items:
        title_words = {
            w for w in re.findall(r"[a-z0-9+#.]+", item.title.lower())
            if w not in stop and len(w) > 2
        }
        if title_words:
            overlap = len(title_words & words) / len(title_words)
            if overlap >= 0.4:
                scored.append((overlap + 0.5, item.item_id))
                continue
        # Fall back to the skills the item teaches.
        for skill_id in item.skills:
            skill = catalog.skills.get(skill_id)
            if not skill:
                continue
            names = {skill.name.lower(), *(a.lower() for a in skill.aliases)}
            if any(n in subject for n in names if len(n) > 3):
                scored.append((item.skills[skill_id], item.item_id))
                break

    scored.sort(key=lambda pair: -pair[0])
    seen: list[str] = []
    for _, item_id in scored:
        if item_id not in seen:
            seen.append(item_id)
    return seen[:limit]


def _join(names: list[str]) -> str:
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + f" and {names[-1]}"


# -- answer builders --------------------------------------------------------

def _answer_ordering(profile, path, items, catalog) -> str:
    if not items:
        first = path.all_items[0]
        return (
            f"The order comes from the prerequisite graph, not from difficulty alone. "
            f"'{first.title}' is first because nothing in your path depends on being "
            f"done before it, and everything else either needs it or needs something "
            f"it unlocks. Within that constraint, foundational material is scheduled "
            f"before applied material and interview-style work comes last."
        )
    item_id = items[0]
    item = catalog.items[item_id]
    dependents = [
        other.title for other in path.all_items
        if item_id in catalog.items[other.item_id].prereqs
    ]
    prereqs = [catalog.items[p].title for p in item.prereqs if p in catalog.items]

    parts = [f"'{item.title}' sits where it does for a specific reason."]
    if dependents:
        parts.append(f"{_join(dependents[:3])} build directly on it, so it has to come first.")
    if prereqs:
        parts.append(f"It in turn needs {_join(prereqs[:3])}, which is why it isn't earlier.")
    if not dependents and not prereqs:
        parts.append(
            "Nothing in your path depends on it, so its position is driven by "
            "difficulty — it's placed where it matches your current level."
        )
    return " ".join(parts)


def _answer_skip(profile, path, items, catalog) -> str:
    if not items:
        return (
            "Tell me which item you'd rather not do — you can also press "
            "'Not for me' on it — and I'll tell you what depends on it before "
            "anything is removed."
        )
    item_id = items[0]
    item = catalog.items[item_id]
    blocked = [
        other.title for other in path.all_items
        if item_id in catalog.items[other.item_id].prereqs
    ]
    covered = [catalog.skill_name(s) for s in list(item.skills)[:3]]

    if blocked:
        return (
            f"You can, but it has consequences: {_join(blocked[:3])} build on "
            f"'{item.title}'. Skipping it means going into those without "
            f"{_join(covered)}. If you already know this material, mark it "
            f"'Too easy' instead — that credits the skills and keeps the rest of "
            f"the path intact."
        )
    return (
        f"Yes — nothing else in your path depends on '{item.title}'. You'd be "
        f"giving up {_join(covered)}, which your goal weights but doesn't require "
        f"first. Press 'Not for me' on it and the path will rebuild without it."
    )


def _answer_duration(profile, path, items, catalog) -> str:
    last = path.milestones[-1] if path.milestones else None
    finish = f" That puts you finishing around {last.ends_on}." if last else ""
    return (
        f"About {path.total_hours} hours of work, which at {profile.hours_per_week:g} "
        f"hours a week is roughly {path.total_weeks} weeks across "
        f"{len(path.milestones)} milestones.{finish} If your available time changes, "
        f"tell me the new number and everything reschedules."
    )


def _answer_faster(profile, path, items, catalog) -> str:
    optional = [i.title for i in path.all_items if not i.is_prerequisite_fill][-3:]
    faster_weeks = round(path.total_hours / max(1.0, profile.hours_per_week * 1.5), 1)
    return (
        f"Three ways to shorten it. Raise your weekly hours — at "
        f"{profile.hours_per_week * 1.5:g} hours it drops from {path.total_weeks} to "
        f"about {faster_weeks} weeks. Mark anything you already know as 'Too easy', "
        f"which credits those skills and removes the item. Or drop lower-priority "
        f"material like {_join(optional)} with 'Not for me'. Prerequisites can't be "
        f"removed without breaking what depends on them."
    )


def _answer_difficulty(profile, path, items, catalog) -> str:
    levels = [i.level for i in path.all_items]
    average = sum(levels) / len(levels) if levels else 1
    names = {1: "beginner", 2: "intermediate", 3: "advanced"}
    starting = path.all_items[0].title if path.all_items else "the first item"
    return (
        f"Your path averages {names.get(round(average), 'intermediate')} difficulty, "
        f"and it opens at the level you told me you're at — '{starting}' assumes no "
        f"prior knowledge of the topic. If something lands too hard, press 'Too hard' "
        f"on it: I'll lower the difficulty target and insert groundwork rather than "
        f"just dropping it."
    )


def _answer_next(profile, path, items, catalog) -> str:
    completed = profile.completed_ids
    ready = [
        i for i in path.all_items
        if i.item_id not in completed
        and not missing_prerequisites(i.item_id, completed, catalog)
    ]
    if not ready:
        return "You've cleared everything that's currently unlocked — nice work."
    first = ready[0]
    unlocks = len(unlocked_by(first.item_id, completed | {first.item_id}, catalog))
    tail = f" Finishing it unlocks {unlocks} more item{'s' if unlocks != 1 else ''}." if unlocks else ""
    others = [i.title for i in ready[1:3]]
    also = f" After that: {_join(others)}." if others else ""
    return (
        f"Start with '{first.title}' — {first.hours} hours from {first.provider}. "
        f"Every prerequisite for it is already behind you.{tail}{also}"
    )


def _answer_progress(profile, path, items, catalog) -> str:
    mastery, _ = compute_mastery(profile, catalog)
    now = readiness(profile, mastery, catalog)
    done = len(profile.completed)
    strongest = [catalog.skill_name(s) for s, v in list(mastery.items())[:3] if v > 0.2]
    tail = f" Your strongest areas right now are {_join(strongest)}." if strongest else ""
    return (
        f"You're at {now:.0%} readiness against {path.role_title or 'your goal'}, with "
        f"{done} item{'s' if done != 1 else ''} completed. Finishing the path takes you "
        f"to about {path.readiness_after:.0%}.{tail}"
    )


def _answer_skills(profile, path, items, catalog) -> str:
    gaps = [g["name"] for g in path.gap_summary[:5]]
    kinds = {"course": 0, "project": 0, "assessment": 0}
    for i in path.all_items:
        kinds[i.kind] = kinds.get(i.kind, 0) + 1
    return (
        f"This path targets {path.gap_count} skills you haven't covered yet — the "
        f"biggest are {_join(gaps[:4])}. You'll do it across {kinds['course']} courses, "
        f"{kinds['project']} hands-on projects and {kinds['assessment']} assessments, so "
        f"you finish with things you've built, not just watched."
    )


def _answer_why_item(profile, path, items, catalog) -> str:
    if not items:
        return (
            "Press 'Why this?' on any item and I'll show the exact scoring "
            "components that placed it there — how much of your skill gap it "
            "closes, how well it fits your level, and what similar learners did."
        )
    item_id = items[0]
    item = catalog.items[item_id]
    path_item = next((i for i in path.all_items if i.item_id == item_id), None)
    covers = (
        [catalog.skill_name(s) for s in list(path_item.covers)[:3]]
        if path_item and path_item.covers else
        [catalog.skill_name(s) for s in list(item.skills)[:3]]
    )
    if path_item and path_item.is_prerequisite_fill:
        return (
            f"'{item.title}' wasn't chosen for its own sake — it was pulled in "
            f"because something else in your path requires it. It gives you "
            f"{_join(covers)}."
        )
    return (
        f"'{item.title}' is there because your goal needs {_join(covers)} and you "
        f"don't have {'them' if len(covers) > 1 else 'it'} yet. Press 'Why this?' on "
        f"the item for the exact score breakdown."
    )


def _answer_overview(profile, path, items, catalog) -> str:
    phases = "; ".join(f"{m.index}) {m.title}" for m in path.milestones)
    return (
        f"Your path to {path.role_title or 'your goal'} is {len(path.all_items)} items, "
        f"{path.total_hours} hours, about {path.total_weeks} weeks at "
        f"{profile.hours_per_week:g} hours a week. It runs in {len(path.milestones)} "
        f"phases — {phases}. It should take you from {path.readiness_before:.0%} to "
        f"{path.readiness_after:.0%} readiness."
    )


def _answer_general(profile, path, items, catalog) -> str:
    if items:
        return _answer_why_item(profile, path, items, catalog)
    return (
        f"I can explain why anything is in your path, what order it runs in and why, "
        f"how long it takes, what happens if you skip something, or what to do next. "
        f"Your path to {path.role_title or 'your goal'} is currently "
        f"{len(path.all_items)} items over about {path.total_weeks} weeks."
    )


BUILDERS = {
    "ordering": _answer_ordering,
    "skip": _answer_skip,
    "duration": _answer_duration,
    "faster": _answer_faster,
    "difficulty": _answer_difficulty,
    "next": _answer_next,
    "progress": _answer_progress,
    "skills": _answer_skills,
    "why_item": _answer_why_item,
    "overview": _answer_overview,
    "general": _answer_general,
}


def answer(
    profile: LearnerProfile, path, message: str, catalog: Catalog = CATALOG
) -> Answer:
    """Answer one learner question about their generated path."""
    intent = classify(message)
    items = find_items(message, path, catalog)
    text = BUILDERS[intent](profile, path, items, catalog)

    narrated = LLM.narrate(
        text,
        f"The learner asked: {message!r}. Rewrite this answer in a warm, direct "
        f"voice. Keep every fact, number and item name exactly as given.",
    )
    return Answer(text=narrated or text, intent=f"answer_{intent}", item_ids=items)
