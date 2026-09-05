"""Resource links and interest capture — both named in the brief."""

from app.links import INTERNAL_PROVIDERS, resource_url
from app.ml.conversation import Session, respond
from app.ml.profiler import LearnerProfile
from app.serializers import catalog_item_to_dict
from app.store import CATALOG


def test_every_external_item_has_somewhere_to_go():
    """A recommendation you cannot act on is half a recommendation."""
    unreachable = [
        item.id for item in CATALOG.items.values()
        if item.provider not in INTERNAL_PROVIDERS
        and resource_url(item.provider, item.title) is None
    ]
    assert not unreachable, f"no resource link for: {unreachable[:5]}"


def test_internal_items_have_no_link():
    for item in CATALOG.items.values():
        if item.provider in INTERNAL_PROVIDERS:
            assert resource_url(item.provider, item.title) is None


def test_links_are_https_and_encoded():
    url = resource_url("Coursera", "Machine Learning Specialization")
    assert url.startswith("https://")
    assert " " not in url


def test_serialized_items_expose_the_link():
    assert "url" in catalog_item_to_dict("ml-101")


def test_named_topics_are_captured_as_interests():
    """The brief asks profiling to capture interests, not only the role."""
    session = Session(id="i", profile=LearnerProfile(id="i"))
    respond(session, "I want to be an ML engineer, I'm really interested in computer vision and NLP")
    interests = session.profile.interests
    assert "Computer Vision" in interests
    assert "Natural Language Processing" in interests


def test_answers_to_prompts_do_not_become_interests():
    session = Session(id="j", profile=LearnerProfile(id="j"))
    respond(session, "I want to become a data scientist")
    before = list(session.profile.interests)
    respond(session, "beginner")
    respond(session, "nothing")
    assert session.profile.interests == before
