"""End-to-end HTTP behaviour."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture
def ready_session(client):
    """A session driven through the chat flow until a path exists."""
    session_id = client.post("/api/session").json()["session_id"]
    for message in (
        "I want to become a machine learning engineer",
        "some grounding",
        "I did Python for Everybody and Intro to Machine Learning",
        "12 hours a week hands-on",
    ):
        client.post(f"/api/session/{session_id}/chat", json={"message": message})
    return session_id


def test_health_and_meta(client):
    assert client.get("/api/health").json() == {"status": "ok"}
    meta = client.get("/api/meta").json()
    assert meta["catalog"]["items"] == 238
    assert meta["llm"]["enabled"] in (True, False)


def test_unknown_session_is_404(client):
    assert client.get("/api/session/deadbeef/path").status_code == 404


def test_path_before_goal_is_409(client):
    session_id = client.post("/api/session").json()["session_id"]
    response = client.get(f"/api/session/{session_id}/path")
    assert response.status_code == 409


def test_chat_flow_produces_a_path(client, ready_session):
    path = client.get(f"/api/session/{ready_session}/path").json()
    assert path["role_title"] == "Machine Learning Engineer"
    assert 3 <= len(path["milestones"]) <= 5
    assert path["total_hours"] > 0
    assert path["narrative"]["strategy"]


def test_dashboard_shape(client, ready_session):
    data = client.get(f"/api/session/{ready_session}/dashboard").json()
    assert 0.0 <= data["readiness"] <= 1.0
    assert data["skills"]["by_category"]
    assert len(data["next_actions"]) <= 4
    for action in data["next_actions"]:
        assert {"item_id", "title", "kind", "hours"} <= set(action)


def test_explanation_is_grounded(client, ready_session):
    path = client.get(f"/api/session/{ready_session}/path").json()
    item_id = path["milestones"][0]["items"][0]["item_id"]
    explanation = client.get(f"/api/session/{ready_session}/explain/{item_id}").json()
    assert explanation["headline"]
    assert explanation["reasons"]
    assert explanation["source"] in ("claude", "template")
    # Every component weight the ranker used is disclosed.
    assert set(explanation["evidence"]["weights"]) == {
        "coverage", "semantic", "collab", "level_fit", "quality", "modality",
    }


def test_explain_unknown_item_is_404(client, ready_session):
    assert client.get(f"/api/session/{ready_session}/explain/nope").status_code == 404


def test_completion_feedback_regenerates_and_advances_progress(client, ready_session):
    before = client.get(f"/api/session/{ready_session}/dashboard").json()
    path = client.get(f"/api/session/{ready_session}/path").json()
    item_id = path["milestones"][0]["items"][0]["item_id"]

    response = client.post(
        f"/api/session/{ready_session}/feedback",
        json={"kind": "completion", "item_id": item_id, "score": 0.9},
    ).json()
    assert response["regenerated"]
    assert response["path"] is not None

    after = client.get(f"/api/session/{ready_session}/dashboard").json()
    assert after["readiness"] > before["readiness"]


def test_path_progress_advances_as_items_are_completed(client, ready_session):
    """Regression: progress read 0% forever.

    The path is regenerated after every completion and excludes finished work,
    so progress measured against the current path alone can never move — the
    dashboard's headline metric was permanently zero even as readiness rose.
    """
    before = client.get(f"/api/session/{ready_session}/dashboard").json()["progress"]
    assert before["items_done"] == 0

    path = client.get(f"/api/session/{ready_session}/path").json()
    first_two = [i["item_id"] for m in path["milestones"] for i in m["items"]][:2]
    for item_id in first_two:
        client.post(
            f"/api/session/{ready_session}/feedback",
            json={"kind": "completion", "item_id": item_id},
        )

    after = client.get(f"/api/session/{ready_session}/dashboard").json()["progress"]
    assert after["items_done"] == 2
    assert after["hours_done"] > 0
    assert after["percent"] > 0
    # Finished work stays counted in the total rather than vanishing from it.
    assert after["items_total"] >= before["items_total"]


def test_pace_feedback_reschedules(client, ready_session):
    before = client.get(f"/api/session/{ready_session}/path").json()["total_weeks"]
    client.post(
        f"/api/session/{ready_session}/feedback",
        json={"kind": "pace", "hours_per_week": 25},
    )
    after = client.get(f"/api/session/{ready_session}/path").json()["total_weeks"]
    assert after < before


def test_feedback_validation(client, ready_session):
    assert client.post(
        f"/api/session/{ready_session}/feedback", json={"kind": "completion"}
    ).status_code == 400
    assert client.post(
        f"/api/session/{ready_session}/feedback", json={"kind": "bogus"}
    ).status_code == 422


def test_profile_form_is_an_alternative_to_chat(client):
    session_id = client.post("/api/session").json()["session_id"]
    response = client.put(
        f"/api/session/{session_id}/profile",
        json={
            "role_id": "devops-engineer", "experience_level": 2, "hours_per_week": 15,
            "completed": [{"item_id": "lin-101", "months_ago": 3}],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["profile"]["role_title"] == "DevOps Engineer"
    assert body["path"]["total_hours"] > 0


def test_profile_rejects_unknown_role_and_items(client):
    session_id = client.post("/api/session").json()["session_id"]
    assert client.put(
        f"/api/session/{session_id}/profile", json={"role_id": "wizard"}
    ).status_code == 400
    assert client.put(
        f"/api/session/{session_id}/profile",
        json={"completed": [{"item_id": "nope"}]},
    ).status_code == 400


def test_catalog_search_is_semantic(client):
    results = client.get("/api/catalog/search", params={"q": "neural networks", "limit": 5}).json()
    assert results["results"]
    titles = " ".join(r["title"].lower() for r in results["results"])
    assert "deep learning" in titles or "neural" in titles


def test_roles_listing(client):
    roles = client.get("/api/roles").json()["roles"]
    assert len(roles) == 22
    assert all(r["top_skills"] for r in roles)
