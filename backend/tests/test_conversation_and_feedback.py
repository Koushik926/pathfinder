"""Dialogue slot-filling, adaptation, and the regressions behind both."""

from app.ml.conversation import Session, _match_known_items, respond
from app.ml.embeddings import SPACE
from app.ml.feedback import apply_completion, apply_pace, apply_reaction
from app.ml.profiler import LearnerProfile, compute_mastery
from app.store import CATALOG


def _session():
    return Session(id="s", profile=LearnerProfile(id="s"))


def test_full_dialogue_reaches_a_complete_profile():
    session = _session()
    for message in (
        "I want to become a machine learning engineer",
        "some grounding",
        "I did Python for Everybody and Intro to Machine Learning",
        "about 12 hours a week, hands-on please",
    ):
        result = respond(session, message)
    assert result["ready"]
    assert session.profile.role_id == "ml-engineer"
    assert session.profile.experience_level == 2
    assert session.profile.hours_per_week == 12
    assert len(session.profile.completed) == 2


def test_a_single_message_can_fill_every_slot():
    session = _session()
    respond(
        session,
        "I'm a beginner who wants to be a frontend developer, "
        "I know nothing yet and can do 6 hours a week watching videos",
    )
    assert session.profile.role_id == "frontend-dev"
    assert session.profile.experience_level == 1
    assert session.profile.hours_per_week == 6
    assert "video" in session.profile.preferred_modalities


def test_ambiguous_goal_asks_instead_of_guessing():
    session = _session()
    result = respond(session, "get better at cloud and deployment stuff")
    assert result["intent"] == "choose_role"
    assert len(result["options"]) > 1

    chosen = result["options"][1]["value"]
    respond(session, result["options"][1]["label"])
    assert session.profile.role_id == chosen


def test_stating_a_goal_is_not_recorded_as_completed_history():
    """Regression: 'machine learning engineer' matched the course title
    'Intro to Machine Learning' and was silently logged as completed work."""
    assert _match_known_items("I want to become a machine learning engineer", CATALOG) == []
    assert "ml-102" in _match_known_items("I did Intro to Machine Learning", CATALOG)


def test_bare_titles_count_once_history_has_been_asked():
    session = _session()
    respond(session, "I want to be a data scientist")
    respond(session, "beginner")
    assert session.last_asked == "history"
    respond(session, "Python for Everybody")
    assert "py-101" in session.profile.completed_ids


def test_unseen_word_forms_still_match():
    """Regression: a word-only TF-IDF returned a zero vector for unseen
    morphology, so the learner got no recommendations at all."""
    vector = SPACE.encode("designing beautiful websites")
    assert not SPACE.is_empty(vector)
    assert SPACE.rank_roles("I like designing beautiful websites")


def test_gibberish_degrades_gracefully():
    session = _session()
    result = respond(session, "zzzz qqqq xxxx")
    assert result["reply"]
    assert not result["ready"]


# -- feedback --------------------------------------------------------------

def test_completion_is_recorded_once(intermediate):
    result = apply_completion(intermediate, "ml-102")
    assert result.regenerate
    again = apply_completion(intermediate, "ml-102")
    assert not again.regenerate


def test_completion_of_unknown_item_is_rejected(intermediate):
    assert not apply_completion(intermediate, "nope").regenerate


def test_too_easy_credits_skills_and_raises_level(intermediate):
    before = intermediate.experience_level
    apply_reaction(intermediate, "ml-102", "too_easy")
    assert intermediate.experience_level > before
    assert intermediate.declared_skills
    mastery, _ = compute_mastery(intermediate)
    assert mastery.get("ml-foundations", 0) > 0


def test_too_hard_lowers_the_difficulty_target(intermediate):
    intermediate.experience_level = 3
    apply_reaction(intermediate, "dl-101", "too_hard")
    assert intermediate.experience_level == 2


def test_loved_biases_the_goal_toward_that_topic(intermediate):
    apply_reaction(intermediate, "ml-109", "loved")
    assert intermediate.goal_skills.get("recsys", 0) > 0


def test_pace_change_is_clamped(intermediate):
    apply_pace(intermediate, 500)
    assert intermediate.hours_per_week == 60
    apply_pace(intermediate, 0.1)
    assert intermediate.hours_per_week == 1
