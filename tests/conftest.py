"""Shared pytest fixtures for Python Academy."""

from __future__ import annotations

import pytest

from app import create_app
from app.extensions import db
from app.seed import seed_all


@pytest.fixture
def app():
    application = create_app("testing")
    with application.app_context():
        seed_all()
        yield application


@pytest.fixture
def client(app):
    return app.test_client()


def register(client, username="tester", email="tester@example.com", password="learnpython123"):
    response = client.post("/api/auth/register", json={
        "username": username, "email": email, "password": password
    })
    assert response.status_code == 200, response.get_json()
    return response.get_json()["user"]


def login(client, identity="tester", password="learnpython123"):
    response = client.post("/api/auth/login", json={"identity": identity, "password": password})
    assert response.status_code == 200, response.get_json()
    return response.get_json()["user"]
