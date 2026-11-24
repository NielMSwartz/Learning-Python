"""Learning API, progress, unlocking and test-result privacy."""

from __future__ import annotations

from app.extensions import db
from app.models import Challenge, Project, Submission, Topic
from tests.conftest import register


def passing_result(item, hidden_secret: str | None = None) -> dict:
    count = len(item.tests) or 1
    results = [{"name": f"Test {i + 1}", "passed": True, "hidden": False,
                "expected": "ok", "actual": "ok", "error": ""} for i in range(count)]
    if hidden_secret:
        results.append({"name": "Hidden 1", "passed": False, "hidden": True,
                        "expected": hidden_secret, "actual": hidden_secret,
                        "error": hidden_secret, "timed_out": False})
        count += 1
    return {"status": "passed" if not hidden_secret else "failed", "passed": count - (1 if hidden_secret else 0),
            "total": count, "results": results, "duration_ms": 42}


def test_pathway_locks_and_unlocks(monkeypatch, client, app):
    register(client)
    import app.api.learning as learning

    monkeypatch.setattr(learning, "grade", lambda files, tests, entrypoint: passing_result(
        type("Item", (), {"tests": tests})()
    ))

    projects = Project.query.filter_by(level=1).order_by(Project.order_index).all()
    assert len(projects) >= 2
    assert client.get(f"/api/projects/{projects[1].slug}").status_code == 403

    for project in projects:
        response = client.post("/api/submit", json={
            "item_type": "project", "slug": project.slug, "code": "print('done')"
        })
        assert response.status_code == 200, response.get_json()
        assert response.get_json()["completed"] is True

    assert client.get(f"/api/projects/{projects[1].slug}").status_code == 200
    levels = client.get("/api/pathway").get_json()["levels"]
    assert levels[0]["completed_count"] == len(projects)
    assert levels[1]["unlocked"] is True

    dashboard = client.get("/api/dashboard").get_json()["dashboard"]
    assert dashboard["stats"]["projects_completed"] == len(projects)
    assert dashboard["level"]["current"] == 2


def test_hidden_test_details_never_reach_the_client(monkeypatch, client, app):
    register(client)
    import app.api.learning as learning

    secret = "TOP_SECRET_ASSERTION_SOURCE"
    monkeypatch.setattr(learning, "grade", lambda files, tests, entrypoint: passing_result(
        type("Item", (), {"tests": tests})(), hidden_secret=secret
    ))
    challenge = Challenge.query.first()

    response = client.post("/api/submit", json={
        "item_type": "challenge", "slug": challenge.slug, "code": "def solve(): pass"
    })
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert secret not in body

    stored = Submission.query.order_by(Submission.id.desc()).first()
    assert secret not in str(stored.results)
    assert stored.results[-1]["hidden"] is True
    assert stored.results[-1]["error"] == ""


def test_challenge_tests_are_not_served_to_browser(client, app):
    register(client)
    challenge = Challenge.query.first()
    data = client.get(f"/api/challenges/{challenge.slug}").get_json()["challenge"]
    assert "tests" not in data
    assert "assertions" not in data


def test_library_search_bookmark_and_exercise(client, app):
    register(client)
    topics = client.get("/api/library?q=variables").get_json()["topics"]
    assert topics and any("variable" in topic["title"].lower() for topic in topics)

    topic = Topic.query.first()
    response = client.post(f"/api/library/{topic.id}/bookmark")
    assert response.get_json()["bookmarked"] is True
    assert any(t["id"] == topic.id for t in client.get("/api/library?bookmarked=1").get_json()["topics"])

    detail = client.get(f"/api/library/{topic.slug}").get_json()
    assert detail["topic"]["explanation"]
    exercise_slug = detail["topic"]["exercises"][0]["slug"]
    exercise = client.get(f"/api/exercises/{exercise_slug}").get_json()["exercise"]
    assert exercise["starter_code"]
    assert "tests" not in exercise


def test_stats_and_achievements(client, app):
    register(client)
    stats = client.get("/api/stats").get_json()["stats"]
    assert len(stats["activity"]) == 30
    assert stats["totals"]["current_level"] == 1
    assert isinstance(stats["achievements"], list)
    assert client.get("/api/achievements").status_code == 200
