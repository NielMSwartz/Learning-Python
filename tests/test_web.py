"""Smoke tests for every server-rendered page and PWA asset."""

from __future__ import annotations

import json
from pathlib import Path

from app.models import Challenge, Exercise, Project, Topic
from tests.conftest import register

ROOT = Path(__file__).resolve().parents[1]


def test_public_pages_and_pwa_assets(client):
    assert client.get("/health").get_json()["status"] == "ok"
    for path in ("/login", "/register", "/forgot", "/offline", "/reset/not-a-real-token"):
        assert client.get(path).status_code == 200, path

    manifest = client.get("/manifest.webmanifest")
    assert manifest.status_code == 200
    assert "manifest+json" in manifest.headers["Content-Type"]
    data = json.loads(manifest.get_data(as_text=True))
    assert data["display"] == "standalone"
    assert len(data["icons"]) >= 2

    sw = client.get("/sw.js")
    assert sw.status_code == 200
    assert b"SHELL_CACHE" in sw.get_data()

    for icon in ("icon-192.png", "icon-512.png", "maskable-512.png"):
        assert (ROOT / "app" / "static" / "icons" / icon).stat().st_size > 1000


def test_all_authenticated_pages_render(client, app):
    register(client)
    project = Project.query.filter_by(level=1).order_by(Project.order_index).first()
    challenge = Challenge.query.first()
    topic = Topic.query.first()
    exercise = Exercise.query.first()

    paths = [
        "/", "/learn", f"/learn/project/{project.slug}", "/challenges",
        f"/challenges/{challenge.slug}", "/library", f"/library/{topic.slug}",
        f"/practice/{exercise.slug}", "/playground", "/ide", "/snippets",
        "/stats", "/profile",
    ]
    for path in paths:
        response = client.get(path)
        assert response.status_code == 200, f"{path}: {response.get_data(as_text=True)[:300]}"
        assert b"Python Academy" in response.get_data()
