"""Authentication and account endpoint tests."""

from __future__ import annotations

from tests.conftest import login, register


def test_registration_login_and_logout(client):
    user = register(client)
    assert user["username"] == "tester"
    assert user["current_level"] == 1

    assert client.get("/api/me").status_code == 200
    assert client.post("/api/auth/logout").status_code == 200
    assert client.get("/api/me").status_code == 401

    assert login(client)["id"] == user["id"]


def test_duplicate_registration_is_rejected(client):
    register(client)
    response = client.post("/api/auth/register", json={
        "username": "other", "email": "tester@example.com", "password": "learnpython123"
    })
    assert response.status_code == 409
    assert "email" in response.get_json()["error"]["message"].lower()


def test_password_change_requires_current_password(client):
    register(client)
    response = client.post("/api/me/password", json={
        "current_password": "wrong", "new_password": "brandnewpassword"
    })
    assert response.status_code == 400

    response = client.post("/api/me/password", json={
        "current_password": "learnpython123", "new_password": "brandnewpassword"
    })
    assert response.status_code == 200

    client.post("/api/auth/logout")
    assert client.post("/api/auth/login", json={
        "identity": "tester", "password": "learnpython123"
    }).status_code == 401
    assert login(client, password="brandnewpassword")["username"] == "tester"


def test_reset_link_flow(client):
    register(client)
    response = client.post("/api/auth/reset-request", json={"email": "tester@example.com"})
    assert response.status_code == 200
    link = response.get_json()["reset_link"]
    token = link.rsplit("/", 1)[-1]

    assert client.post("/api/auth/reset", json={"token": token, "password": "resetpassword1"}).status_code == 200
    # A one-time token cannot be reused.
    assert client.post("/api/auth/reset", json={"token": token, "password": "resetpassword2"}).status_code == 400
