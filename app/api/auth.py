"""Authentication endpoints."""

from __future__ import annotations

import re

from flask import current_app, jsonify
from flask_login import current_user, login_user, logout_user

from ..extensions import db
from ..models import PasswordResetToken, User, utcnow
from ..services.mail import send_password_reset
from . import api_bp
from .utils import body, error, ok, require_fields

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")


def valid_email(value: str) -> bool:
    try:
        from email_validator import validate_email

        validate_email(value, check_deliverability=False)
        return True
    except ImportError:
        return "@" in value and "." in value.split("@")[-1]
    except Exception:
        return False


@api_bp.post("/auth/register")
def register():
    data = body()
    message = require_fields(["username", "email", "password"], data)
    if message:
        return error(message)
    username = data["username"].strip()
    email = data["email"].strip().lower()
    password = data["password"]
    if not USERNAME_RE.match(username):
        return error("Username must be 3-32 characters using letters, numbers, ., _ or -")
    if not valid_email(email):
        return error("Please enter a valid email address")
    if len(password) < 8:
        return error("Password must be at least 8 characters long")
    if User.query.filter_by(username=username).first():
        return error("That username is already taken", 409)
    if User.query.filter_by(email=email).first():
        return error("That email is already registered", 409)

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    login_user(user, remember=True)
    current_app.logger.info("New user registered: %s", username)
    return ok(user=user.public_dict())


@api_bp.post("/auth/login")
def login():
    data = body()
    identity = str(data.get("identity") or data.get("email") or "").strip().lower()
    password = str(data.get("password") or "")
    if not identity or not password:
        return error("Enter your username or email and password")
    user = User.query.filter_by(email=identity).first() or User.query.filter_by(username=identity).first()
    if user is None or not user.check_password(password):
        # Generic message avoids revealing which accounts exist.
        return error("Invalid credentials", 401)
    login_user(user, remember=bool(data.get("remember", True)))
    user.touch()
    db.session.commit()
    return ok(user=user.public_dict())


@api_bp.post("/auth/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return ok(message="Signed out")


@api_bp.post("/auth/reset-request")
def reset_request():
    email = str(body().get("email", "")).strip().lower()
    user = User.query.filter_by(email=email).first()
    response = {"message": "If that email is registered, a reset link has been created."}
    if user:
        token = PasswordResetToken.create(user)
        db.session.commit()
        sent = send_password_reset(user, token)
        if not sent:
            # Self-hosted installs without SMTP still get a usable one-time link.
            response["reset_link"] = f"/reset/{token}"
            response["message"] += " Email delivery is not configured, so the link is shown below."
    return ok(**response)


@api_bp.post("/auth/reset")
def reset_password():
    data = body()
    token = str(data.get("token", ""))
    password = str(data.get("password", ""))
    if len(password) < 8:
        return error("Password must be at least 8 characters long")
    row = PasswordResetToken.find_valid(token)
    if row is None:
        return error("This reset link is invalid or has expired", 400)
    row.user.set_password(password)
    row.used_at = utcnow()
    db.session.commit()
    return ok(message="Password updated. You can sign in now.")
