"""Current user, preferences and learning statistics endpoints."""

from __future__ import annotations

from flask import jsonify
from flask_login import current_user

from ..extensions import db
from ..models import User
from ..services.progress import achievements as achievement_list
from ..services.progress import stats as build_stats
from . import api_bp
from .utils import api_login_required, body, error, ok


@api_bp.get("/me")
@api_login_required
def me():
    return ok(user=current_user.public_dict())


@api_bp.patch("/me")
@api_login_required
def update_me():
    data = body()
    username = str(data.get("username", current_user.username)).strip()
    email = str(data.get("email", current_user.email)).strip().lower()
    if len(username) < 3 or len(username) > 32 or not username.replace("_", "").replace("-", "").replace(".", "").isalnum():
        return error("Username must be 3-32 letters, numbers, ., _ or -")
    if "@" not in email or "." not in email.split("@")[-1]:
        return error("Please enter a valid email address")
    if User.query.filter(User.id != current_user.id, User.username.ilike(username)).first():
        return error("That username is already taken", 409)
    if User.query.filter(User.id != current_user.id, User.email.ilike(email)).first():
        return error("That email is already registered", 409)
    current_user.username = username
    current_user.email = email
    db.session.commit()
    return ok(user=current_user.public_dict())


@api_bp.post("/me/password")
@api_login_required
def change_password():
    data = body()
    current = str(data.get("current_password", ""))
    new = str(data.get("new_password", ""))
    if not current_user.check_password(current):
        return error("Your current password is incorrect", 400)
    if len(new) < 8:
        return error("New password must be at least 8 characters long")
    current_user.set_password(new)
    db.session.commit()
    return ok(message="Password updated")


@api_bp.patch("/me/preferences")
@api_login_required
def preferences():
    current_user.apply_preferences(body())
    db.session.commit()
    return ok(user=current_user.public_dict())


@api_bp.post("/activity")
@api_login_required
def activity():
    """Heartbeat from the editor; counts focused coding time."""
    try:
        seconds = int(body().get("seconds", 0))
    except (TypeError, ValueError):
        return error("Invalid duration")
    current_user.add_coding_time(seconds)
    db.session.commit()
    return ok(streak=current_user.streak, total_seconds=current_user.total_coding_seconds)


@api_bp.get("/stats")
@api_login_required
def stats():
    return ok(stats=build_stats(current_user))


@api_bp.get("/achievements")
@api_login_required
def achievement_endpoint():
    return ok(achievements=achievement_list(current_user))
