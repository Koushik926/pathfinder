"""Reading what learners actually type.

Every case here was found by using the product rather than reading the code.
The one that started it: a learner answered the question "roughly how many
hours a week can you give this?" with "3", and the assistant asked again — the
single most annoying thing a form-filling assistant can do.
"""

import pytest

from app.ml.conversation import (
    RETRY, Session, _extract_hours, _extract_level, respond,
)
from app.ml.profiler import LearnerProfile


def _session():
    return Session(id="s", profile=LearnerProfile(id="s"))


# -- hours ------------------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("3", 3.0), ("10", 10.0),                       # a bare number, the reported bug
    ("about 5", 5.0), ("maybe 4", 4.0), ("i can do 6", 6.0),
    ("3 hours", 3.0), ("10 hrs", 10.0), ("15h", 15.0),
    ("20 hours per week", 20.0), ("around 8 hours a week", 8.0),
    ("one hour", 1.0), ("two hours", 2.0), ("a couple of hours", 2.0),
    ("2-3", 2.5), ("5-6 hours", 5.5),               # a range means the midpoint
])
def test_hours_are_read_when_we_just_asked_for_them(text, expected):
    assert _extract_hours(text, expecting=True) == expected


@pytest.mark.parametrize("text,expected", [
    ("not much", 3.0), ("a lot", 25.0), ("as much as i can", 25.0),
])
def test_vague_amounts_become_a_concrete_pace(text, expected):
    assert _extract_hours(text, expecting=True) == expected


def test_a_bare_number_is_not_hours_when_we_did_not_ask():
    """Context matters: "3" mid-conversation is not a weekly budget."""
    assert _extract_hours("3", expecting=False) is None
    assert _extract_hours("10 hours a week", expecting=False) == 10.0


# -- level ------------------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("beginner", 1), ("total noob", 1), ("zero", 1), ("none", 1),
    ("not much", 1), ("from scratch", 1),
    ("some grounding", 2), ("i know a bit", 2), ("ive done some", 2),
    ("medium", 2), ("average", 2), ("intermediate", 2),
    ("experienced", 3), ("pro", 3), ("expert", 3),
])
def test_level_reads_how_people_actually_answer(text, expected):
    assert _extract_level(text) == expected


# -- the conversation cannot trap you ---------------------------------------

def test_the_reported_conversation_now_completes():
    """dsa -> Some grounding -> a course title -> "3"."""
    session = _session()
    for message in ("dsa", "Some grounding", "Data Structures Easy to Advanced", "3"):
        result = respond(session, message)
    assert result["ready"]
    assert session.profile.hours_per_week == 3.0


def test_naming_a_technology_answers_the_history_question():
    """People answer "what have you done?" with "python", not with a course title."""
    session = _session()
    respond(session, "data science")
    respond(session, "medium")
    result = respond(session, "python")
    assert "history" not in result["missing_slots"]
    assert session.profile.declared_skills


def test_a_slot_is_never_asked_more_than_twice():
    session = _session()
    respond(session, "dsa")
    asks = []
    for _ in range(6):
        result = respond(session, "k")
        asks.append(result["intent"])
    assert asks.count("ask_level") <= 2, f"level asked {asks.count('ask_level')} times"


def test_a_question_is_never_repeated_word_for_word():
    """Repeating verbatim reads as though nothing you said registered."""
    session = _session()
    respond(session, "dsa")
    first = respond(session, "k")["reply"]
    second = respond(session, "k")["reply"]
    assert first != second
    assert RETRY["level"] in second or second != first


@pytest.mark.parametrize("answer", ["k", "?", "asdf", "dunno", "no"])
def test_even_an_unhelpful_learner_reaches_a_plan(answer):
    """No answer, however useless, may leave someone stuck forever."""
    session = _session()
    for turn in range(15):
        if respond(session, answer)["ready"]:
            return
    pytest.fail(f"answering {answer!r} never produced a plan in 15 turns")


def test_every_slot_question_offers_something_to_tap():
    session = _session()
    result = respond(session, "i want to become a data scientist")
    seen = 0
    for _ in range(3):
        if result["intent"].startswith("ask_") and result["options"]:
            seen += 1
        result = respond(session, "k")
    assert seen >= 1, "slot questions should offer quick replies"


# -- greetings --------------------------------------------------------------

def test_a_greeting_is_not_a_career():
    """Reported: saying "hello" offered DevOps Engineer, Penetration Tester and
    Security Analyst. The embedding scored "hello" at 0.31 against DevOps —
    character-n-gram noise, presented to the learner as a considered guess."""
    session = _session()
    result = respond(session, "hello")
    assert result["intent"] == "ask_goal"
    assert not result["options"], "a greeting must not produce role suggestions"
    assert session.profile.role_id is None


@pytest.mark.parametrize("greeting", ["hi", "hii", "hey", "good morning", "thanks", "ok"])
def test_pleasantries_are_answered_not_matched(greeting):
    session = _session()
    assert respond(session, greeting)["intent"] == "ask_goal"


def test_a_greeting_with_a_goal_in_it_is_still_a_goal():
    session = _session()
    respond(session, "hi, I want to learn Python")
    assert session.profile.role_id or session.profile.goal_skills


def test_restating_the_goal_beats_the_options_on_offer():
    """Reported: mid-disambiguation the learner typed "dsa" — which resolves
    perfectly — and was shown the same three unrelated roles again, because the
    match was rejected for not being one of the options offered."""
    session = _session()
    respond(session, "hello")
    respond(session, "something with data")     # forces a disambiguation
    respond(session, "dsa")
    assert session.profile.role_id == "sde-placement"


def test_small_talk_cannot_loop_forever():
    """The greeting path is bounded like every other question."""
    session = _session()
    for turn in range(15):
        if respond(session, "ok")["ready"]:
            return
    pytest.fail("answering 'ok' forever never produced a plan")


def test_switching_careers_targets_the_destination():
    """"switch from web dev to ML" names two roles and means the second.
    Longest-alias-wins has no sense of direction and answered with the one
    they were leaving."""
    from app.ml.embeddings import SPACE

    assert SPACE.rank_roles("i want to switch from web dev to ML", 1)[0][0] == "ml-engineer"
    assert SPACE.rank_roles("moving from testing into data science", 1)[0][0] == "data-scientist"
    assert SPACE.rank_roles("switch from frontend to devops", 1)[0][0] == "devops-engineer"
    # A plain goal with no direction still resolves normally.
    assert SPACE.rank_roles("web development", 1)[0][0] == "frontend-dev"


def test_noise_is_never_accepted_as_a_named_skill():
    """"asdf qwer" scored 0.80 against BI tools on character n-grams alone."""
    session = _session()
    respond(session, "asdf qwer")
    assert not session.profile.goal_skills


def test_a_skill_only_goal_still_gets_a_titled_path():
    from app.ml.planner import generate_path

    session = _session()
    for message in ("hi, I want to learn Python", "beginner", "nothing", "6"):
        respond(session, message)
    path = generate_path(session.profile)
    assert path.role_title, "a path with no career role still needs a name"
    assert path.all_items


# -- "I don't know" ---------------------------------------------------------

@pytest.mark.parametrize("said", [
    "don't know", "dont know", "no idea", "not sure", "dunno", "idk",
    "anything", "you decide", "help me choose", "confused",
    "suggest something", "what should i learn",
])
def test_uncertainty_gets_real_choices_not_noise(said):
    """Reported: "don't know" offered MLOps Engineer, ML Engineer and DevOps
    Engineer. None of those came from anything the learner said — every one of
    these phrases contains zero words the catalog recognises, and the scores
    were character-n-gram artefacts presented as considered suggestions."""
    session = _session()
    result = respond(session, said)
    assert result["intent"] == "choose_role"
    assert len(result["options"]) >= 4, "not knowing deserves real options"
    assert session.profile.role_id is None


def test_a_score_with_no_real_word_behind_it_is_not_a_match():
    """"dunno" scored 0.56 against Embedded Engineer — above the threshold at
    which we commit without asking. It would have picked a career silently."""
    from app.ml.embeddings import SPACE

    for noise in ("dunno", "don't know", "asdf qwer", "zzz", "idk"):
        assert SPACE.lexical_signal(noise) == 0
        assert SPACE.rank_roles(noise, 3) == [], f"{noise!r} produced a role match"


@pytest.mark.parametrize("goal,expected", [
    ("dsa", "sde-placement"), ("ml", "ml-engineer"),
    ("data science", "data-scientist"), ("web development", "frontend-dev"),
    ("cyber security", "pentester"), ("i want to make apps", "mobile-dev"),
])
def test_real_goals_still_resolve(goal, expected):
    """The vocabulary gate must not cost us any genuine match."""
    session = _session()
    respond(session, goal)
    assert session.profile.role_id == expected


def test_unseen_word_forms_survive_the_vocabulary_gate():
    """"designing beautiful websites" uses no catalog word verbatim but does
    share vocabulary — it must still reach a goal."""
    session = _session()
    respond(session, "designing beautiful websites")
    assert session.profile.role_id or session.profile.goal_skills
