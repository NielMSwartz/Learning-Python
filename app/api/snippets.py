"""Code snippet manager endpoints."""

from __future__ import annotations

from flask import request
from flask_login import current_user

from ..extensions import db
from ..models import Snippet, utcnow
from . import api_bp
from .utils import api_login_required, body, clean_tags, error, ok


def own_snippet(snippet_id: int) -> Snippet | None:
    return Snippet.query.filter_by(id=snippet_id, user_id=current_user.id).first()


def apply_data(snippet: Snippet, data: dict) -> str | None:
    if "name" in data:
        name = str(data["name"]).strip()[:160]
        if not name:
            return "Name is required"
        snippet.name = name
    if "code" in data:
        snippet.code = str(data["code"])[:100_000]
    if "description" in data:
        snippet.description = str(data["description"])[:2_000]
    if "category" in data:
        snippet.category = str(data["category"]).strip()[:80] or "General"
    if "tags" in data:
        snippet.tags = clean_tags(data["tags"])
    return None


@api_bp.get("/snippets")
@api_login_required
def list_snippets():
    query = request.args.get("q", "").strip().lower()
    category = request.args.get("category", "").strip().lower()
    tag = request.args.get("tag", "").strip().lower()
    snippets = (
        Snippet.query.filter_by(user_id=current_user.id)
        .order_by(Snippet.updated_at.desc())
        .all()
    )
    results = []
    for snippet in snippets:
        haystack = f"{snippet.name} {snippet.description} {snippet.category} {' '.join(snippet.tags or [])}".lower()
        if query and query not in haystack and query not in snippet.code.lower():
            continue
        if category and category not in snippet.category.lower():
            continue
        if tag and tag not in [t.lower() for t in snippet.tags or []]:
            continue
        results.append(snippet.to_dict())
    categories = sorted({s.category for s in snippets})
    return ok(snippets=results, categories=categories)


@api_bp.post("/snippets")
@api_login_required
def create_snippet():
    data = body()
    snippet = Snippet(user_id=current_user.id, name="Untitled snippet", category="General")
    message = apply_data(snippet, data)
    if message:
        return error(message)
    if not snippet.name.strip():
        return error("Name is required")
    db.session.add(snippet)
    db.session.commit()
    return ok(snippet=snippet.to_dict())


@api_bp.get("/snippets/<int:snippet_id>")
@api_login_required
def get_snippet(snippet_id: int):
    snippet = own_snippet(snippet_id)
    if snippet is None:
        return error("Snippet not found", 404)
    return ok(snippet=snippet.to_dict())


@api_bp.put("/snippets/<int:snippet_id>")
@api_login_required
def update_snippet(snippet_id: int):
    snippet = own_snippet(snippet_id)
    if snippet is None:
        return error("Snippet not found", 404)
    message = apply_data(snippet, body())
    if message:
        return error(message)
    snippet.updated_at = utcnow()
    db.session.commit()
    return ok(snippet=snippet.to_dict())


@api_bp.delete("/snippets/<int:snippet_id>")
@api_login_required
def delete_snippet(snippet_id: int):
    snippet = own_snippet(snippet_id)
    if snippet is None:
        return error("Snippet not found", 404)
    db.session.delete(snippet)
    db.session.commit()
    return ok(message="Snippet deleted")
