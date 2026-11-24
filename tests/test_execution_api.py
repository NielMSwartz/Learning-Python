"""Playground/IDE execution endpoints and preferences."""

from __future__ import annotations

from tests.conftest import register


def test_execute_endpoint_returns_sandbox_output(monkeypatch, client, app):
    register(client)
    import app.api.execution as execution

    captured = {}

    def fake_run(files, entrypoint="main.py", stdin=""):
        captured.update(files=files, entrypoint=entrypoint, stdin=stdin)
        return {"status": "ok", "stdout": "formatted output\n", "stderr": "", "duration_ms": 3}

    monkeypatch.setattr(execution, "run_code", fake_run)
    response = client.post("/api/execute", json={
        "code": "print('hi')", "stdin": "Ada\n", "files": {"helpers.py": "VALUE = 1"},
        "entrypoint": "main.py"
    })
    assert response.status_code == 200
    assert response.get_json()["stdout"] == "formatted output\n"
    assert captured["files"]["helpers.py"] == "VALUE = 1"
    assert captured["stdin"] == "Ada\n"


def test_execute_endpoint_validates_input(client, app):
    register(client)
    assert client.post("/api/execute", json={"code": "   "}).status_code == 400
    assert client.post("/api/execute", json={"code": "print(1)", "entrypoint": "missing.py"}).status_code == 400


def test_format_endpoint_uses_black(client, app):
    register(client)
    response = client.post("/api/format", json={"code": "x=1\nprint( x )\n"})
    assert response.status_code == 200
    assert response.get_json()["code"] == 'x = 1\nprint(x)\n'


def test_activity_and_preferences(client, app):
    register(client)
    response = client.post("/api/activity", json={"seconds": 120})
    assert response.status_code == 200
    assert response.get_json()["total_seconds"] == 120

    response = client.patch("/api/me/preferences", json={
        "theme": "light", "font_size": 18, "tab_size": 2, "line_wrapping": True
    })
    assert response.status_code == 200
    user = response.get_json()["user"]
    assert user["theme"] == "light"
    assert user["preferences"]["font_size"] == 18
    assert user["preferences"]["line_wrapping"] is True

    # Invalid values are ignored rather than corrupting preferences.
    response = client.patch("/api/me/preferences", json={"theme": "neon", "font_size": 999})
    assert response.get_json()["user"]["theme"] == "light"
    assert response.get_json()["user"]["preferences"]["font_size"] == 18
