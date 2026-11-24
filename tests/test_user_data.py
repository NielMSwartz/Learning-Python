"""Per-user data isolation for IDE projects and snippets."""

from __future__ import annotations

from tests.conftest import register


def test_ide_projects_are_private(client, app):
    register(client, "alice", "alice@example.com")
    created = client.post("/api/ide/projects", json={"name": "Alice project"}).get_json()["project"]
    project_id = created["id"]
    file_id = created["files"][0]["id"]
    assert created["files"][0]["path"] == "main.py"

    other = app.test_client()
    register(other, "bob", "bob@example.com")
    assert other.get(f"/api/ide/projects/{project_id}").status_code == 404
    assert other.put(f"/api/ide/files/{file_id}", json={"content": "stolen"}).status_code == 404
    assert other.post(f"/api/ide/projects/{project_id}/files", json={"path": "evil.py"}).status_code == 404
    assert other.get("/api/ide/projects").get_json()["projects"] == []


def test_ide_save_and_file_validation(client, app):
    register(client)
    created = client.post("/api/ide/projects", json={"name": "Scratch"}).get_json()["project"]
    project_id = created["id"]

    added = client.post(f"/api/ide/projects/{project_id}/files", json={
        "path": "utils/helpers.py", "content": "def helper():\n    return 42\n"
    })
    assert added.status_code == 200

    assert client.post(f"/api/ide/projects/{project_id}/files", json={"path": "../escape.py"}).status_code == 400
    assert client.post(f"/api/ide/projects/{project_id}/files", json={"path": "/absolute.py"}).status_code == 400

    saved = client.post(f"/api/ide/projects/{project_id}/save", json={
        "files": {"main.py": "print('saved')", "notes.txt": "remember this"}
    })
    assert saved.status_code == 200
    paths = [file["path"] for file in saved.get_json()["project"]["files"]]
    assert paths == ["main.py", "notes.txt"]


def test_snippets_are_private_and_searchable(client, app):
    register(client, "carol", "carol@example.com")
    created = client.post("/api/snippets", json={
        "name": "Word frequencies", "code": "from collections import Counter\n",
        "category": "Data", "tags": "collections, counter"
    }).get_json()["snippet"]
    assert created["tags"] == ["collections", "counter"]

    assert client.get("/api/snippets?q=counter").get_json()["snippets"]
    assert client.get("/api/snippets?tag=collections").get_json()["snippets"]

    other = app.test_client()
    register(other, "dave", "dave@example.com")
    assert other.get(f"/api/snippets/{created['id']}").status_code == 404
    assert other.delete(f"/api/snippets/{created['id']}").status_code == 404
