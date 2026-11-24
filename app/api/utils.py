"""Shared helpers for JSON API endpoints."""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from flask import jsonify, request
from flask_login import current_user


def body() -> dict[str, Any]:
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def error(message: str, status: int = 400):
    return jsonify(error={"code": status, "message": message}), status


def ok(**kwargs):
    return jsonify(kwargs)


def require_fields(fields: list[str], data: dict[str, Any]) -> str | None:
    for field in fields:
        if not isinstance(data.get(field), str) or not data[field].strip():
            return f"{field.replace('_', ' ').capitalize()} is required"
    return None


def api_login_required(view: Callable) -> Callable:
    """JSON-flavoured login requirement (avoids redirects on the API)."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return error("Please sign in to continue", 401)
        return view(*args, **kwargs)
    return wrapper


def clean_tags(value: Any) -> list[str]:
    if isinstance(value, str):
        value = [part.strip() for part in value.split(",")]
    if not isinstance(value, list):
        return []
    tags = []
    for item in value:
        if not isinstance(item, str):
            continue
        tag = item.strip()[:40]
        if tag and tag not in tags:
            tags.append(tag)
    return tags[:10]
