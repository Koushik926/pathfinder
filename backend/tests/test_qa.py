"""The assistant must answer questions about a path, not just build one.

The brief asks for an assistant that explains recommendations *and answers
learner queries*. Before this existed, every message after setup returned the
same "that's everything I need" line — the assistant went deaf exactly when
the learner had something to ask.
"""

import pytest

from app.ml import qa
from app.ml.conversation import Session, respond
from app.ml.planner import generate_path
from app.ml.profiler import LearnerProfile
from app.store import CATALOG


@pytest.fixture(scope="module")
def path_and_profile():
    profile = LearnerProfile(
        id="q", role_id="ml-engineer", goal_text="become a machine learning engineer",
        experience_level=1, hours_per_week=12,
    )
    return profile, generate_path(profile)


@pytest.mark.parametrize("message,expected", [
    ("why is linear algebra before deep learning?", "ordering"),
    ("can I skip the Python part?", "skip"),
    ("do I really need statistics?", "skip"),
    ("how long will this take me?", "duration"),
    ("can I go faster?", "faster"),
    ("is this too hard for me?", "difficulty"),
    ("what should I do first?", "next"),
    ("how am I doing?", "progress"),
    ("what will I actually learn?", "skills"),
    ("why do I need vector databases?", "why_item"),
    ("explain my plan", "overview"),
])
def test_intents_classify(message, expected):
    assert qa.classify(message) == expected


def test_every_intent_has_a_builder():
    assert set(name for name, _ in qa.INTENT_PATTERNS) | {"general"} == set(qa.BUILDERS)


def test_answers_are_non_empty_and_specific(path_and_profile):
    profile, path = path_and_profile
    for message, _ in [(m, i) for m, i in [
        ("what should I do first?", "next"),
        ("how long will this take?", "duration"),
        ("explain my plan", "overview"),
        ("what will I learn?", "skills"),
    ]]:
        answer = qa.answer(profile, path, message)
        assert len(answer.text) > 40, message
        assert answer.intent.startswith("answer_")


def test_duration_answer_uses_the_real_schedule(path_and_profile):
    profile, path = path_and_profile
    text = qa.answer(profile, path, "how long will this take?").text
    assert str(path.total_hours) in text
    assert str(path.total_weeks) in text


def test_next_answer_only_suggests_unlocked_work(path_and_profile):
    profile, path = path_and_profile
    text = qa.answer(profile, path, "what should I do first?").text
    first_ready = next(i for i in path.all_items if not i.prereqs or all(
        p not in {x.item_id for x in path.all_items} for p in i.prereqs))
    assert first_ready.title in text or path.all_items[0].title in text


def test_ordering_question_is_about_the_named_item(path_and_profile):
    """'why is X before Y' is a question about X, and answering about Y reads
    as though the assistant misunderstood."""
    profile, path = path_and_profile
    titles = {i.title for i in path.all_items}
    if "Linear Algebra for Machine Learning" in titles:
        text = qa.answer(profile, path, "why is linear algebra before deep learning?").text
        assert "Linear Algebra" in text


def test_skip_answer_names_what_would_break(path_and_profile):
    profile, path = path_and_profile
    blocking = next(
        (i for i in path.all_items
         if any(i.item_id in CATALOG.items[o.item_id].prereqs for o in path.all_items)),
        None,
    )
    if blocking:
        text = qa.answer(profile, path, f"can I skip {blocking.title}?").text
        assert "consequence" in text.lower() or "build on" in text.lower()


# -- integration through the conversation ----------------------------------

def _ready_session():
    session = Session(id="s", profile=LearnerProfile(id="s"))
    for message in ("I want to become a machine learning engineer", "beginner",
                    "nothing", "12 hours a week"):
        respond(session, message)
    session.path = generate_path(session.profile)
    return session


def test_questions_after_setup_are_answered_not_repeated():
    """Regression: every post-setup message returned the same canned reply."""
    session = _ready_session()
    replies = []
    for question in ("what should I do first?", "how long will this take?", "explain my plan"):
        replies.append(respond(session, question)["reply"])
    assert len(set(replies)) == 3, "the assistant repeated itself instead of answering"
    assert all(len(r) > 40 for r in replies)


def test_stating_new_hours_reschedules_rather_than_answering():
    session = _ready_session()
    result = respond(session, "i only have 5 hours a week now")
    assert result["reschedule"] is True
    assert session.profile.hours_per_week == 5
