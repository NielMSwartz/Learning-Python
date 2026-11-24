"""Dashboard, learning pathway, library, challenges and grading endpoints."""

from __future__ import annotations

from flask import request
from flask_login import current_user

from ..extensions import db
from ..models import Bookmark, Challenge, Exercise, Progress, Project, Topic
from ..services import progress as progress_service
from ..services.executor_client import ExecutionUnavailable, grade
from . import api_bp
from .utils import api_login_required, body, error, ok


@api_bp.get("/dashboard")
@api_login_required
def dashboard():
    return ok(dashboard=progress_service.dashboard(current_user))


@api_bp.get("/pathway")
@api_login_required
def pathway():
    return ok(levels=progress_service.pathway(current_user))


@api_bp.get("/projects/<slug>")
@api_login_required
def project_detail(slug: str):
    project = Project.query.filter_by(slug=slug).first_or_404()
    if not progress_service.project_unlocked(current_user, project):
        return error("Complete the previous project to unlock this one", 403)
    progress = Progress.for_item(
        current_user.id, "project", project.id
    )
    return ok(
        project=project.to_dict(detailed=True),
        status=progress.status if progress else "not_started",
        score=progress.score if progress else 0,
        last_code=progress.last_code if progress else project.starter_code,
        related_topics=[t.to_dict() for t in Topic.query.filter_by(level=project.level).order_by(Topic.order_index).all()],
    )


@api_bp.get("/library")
@api_login_required
def library():
    query = request.args.get("q", "").strip().lower()
    level = request.args.get("level", type=int)
    category = request.args.get("category", "").strip().lower()
    bookmarked_only = request.args.get("bookmarked") == "1"
    topics = Topic.query.order_by(Topic.level, Topic.order_index).all()
    bookmarked_ids = {b.topic_id for b in Bookmark.query.filter_by(user_id=current_user.id).all()}
    results = []
    for topic in topics:
        if level and topic.level != level:
            continue
        if category and category not in topic.category.lower():
            continue
        if bookmarked_only and topic.id not in bookmarked_ids:
            continue
        if query and query not in f"{topic.title} {topic.summary} {topic.category}".lower():
            continue
        item = topic.to_dict()
        item["bookmarked"] = topic.id in bookmarked_ids
        results.append(item)
    categories = sorted({t.category for t in Topic.query.all()})
    return ok(topics=results, categories=categories)


@api_bp.get("/library/<slug>")
@api_login_required
def topic_detail(slug: str):
    topic = Topic.query.filter_by(slug=slug).first_or_404()
    bookmark = Bookmark.query.filter_by(user_id=current_user.id, topic_id=topic.id).first()
    unlocked = progress_service.mark_topic_studied(current_user, topic)
    data = topic.to_dict(detailed=True)
    data["bookmarked"] = bookmark is not None
    return ok(topic=data, achievements_unlocked=unlocked)


@api_bp.post("/library/<int:topic_id>/bookmark")
@api_login_required
def toggle_bookmark(topic_id: int):
    topic = db.session.get(Topic, topic_id)
    if topic is None:
        return error("Topic not found", 404)
    bookmark = Bookmark.query.filter_by(user_id=current_user.id, topic_id=topic_id).first()
    if bookmark:
        db.session.delete(bookmark)
        bookmarked = False
    else:
        db.session.add(Bookmark(user_id=current_user.id, topic_id=topic_id))
        bookmarked = True
    db.session.commit()
    return ok(bookmarked=bookmarked)


@api_bp.get("/exercises/<slug>")
@api_login_required
def exercise_detail(slug: str):
    exercise = Exercise.query.filter_by(slug=slug).first_or_404()
    data = exercise.to_dict()
    data["topic"] = exercise.topic.to_dict()
    progress = Progress.for_item(
        current_user.id, "exercise", exercise.id
    )
    data["last_code"] = progress.last_code if progress else exercise.starter_code
    return ok(exercise=data)


@api_bp.get("/challenges")
@api_login_required
def challenges():
    level = request.args.get("level", type=int)
    category = request.args.get("category", "").strip().lower()
    query = request.args.get("q", "").strip().lower()
    done = progress_service.completed_ids(current_user.id, "challenge")
    items = []
    for challenge in Challenge.query.order_by(Challenge.level, Challenge.order_index).all():
        if level and challenge.level != level:
            continue
        if category and category not in challenge.category.lower():
            continue
        if query and query not in f"{challenge.title} {challenge.description}".lower():
            continue
        item = challenge.public_dict()
        item["completed"] = challenge.id in done
        items.append(item)
    categories = sorted({c.category for c in Challenge.query.all()})
    return ok(challenges=items, categories=categories)


@api_bp.get("/challenges/<slug>")
@api_login_required
def challenge_detail(slug: str):
    challenge = Challenge.query.filter_by(slug=slug).first_or_404()
    progress = Progress.for_item(
        current_user.id, "challenge", challenge.id
    )
    return ok(
        challenge=challenge.public_dict(detailed=True),
        last_code=progress.last_code if progress else challenge.starter_code,
        status=progress.status if progress else "not_started",
        score=progress.score if progress else 0,
    )


def _resolve_item(item_type: str, identifier: str):
    if item_type == "project":
        return Project.query.filter_by(slug=identifier).first()
    if item_type == "challenge":
        return Challenge.query.filter_by(slug=identifier).first()
    if item_type == "exercise":
        return Exercise.query.filter_by(slug=identifier).first()
    return None


def _sanitize_results(result: dict) -> dict:
    clean = dict(result)
    clean["results"] = [
        {
            "name": row.get("name"),
            "passed": row.get("passed", False),
            "hidden": row.get("hidden", False),
            "expected": "" if row.get("hidden") else row.get("expected", ""),
            "actual": "" if row.get("hidden") else row.get("actual", ""),
            "error": "" if row.get("hidden") else row.get("error", ""),
            "timed_out": row.get("timed_out", False),
        }
        for row in result.get("results", [])
    ]
    return clean


@api_bp.post("/submit")
@api_login_required
def submit():
    data = body()
    item_type = str(data.get("item_type", ""))
    identifier = str(data.get("slug") or data.get("id") or "")
    code = str(data.get("code", ""))
    if item_type not in {"project", "challenge", "exercise"}:
        return error("Unknown submission type")
    item = _resolve_item(item_type, identifier)
    if item is None:
        return error("Learning item not found", 404)
    if item_type == "project" and not progress_service.project_unlocked(current_user, item):
        return error("This project is locked", 403)
    if not code.strip():
        return error("Write some code before submitting")
    if len(code) > 100_000:
        return error("Submission is too large")

    files = {"main.py": code}
    extra = data.get("files")
    if isinstance(extra, dict):
        for name, content in list(extra.items())[:20]:
            if isinstance(name, str) and isinstance(content, str) and name.endswith(".py"):
                files[name] = content[:100_000]

    try:
        result = grade(files, item.tests or [], entrypoint="main.py")
    except ExecutionUnavailable as exc:
        return error(str(exc), 503)

    safe_result = _sanitize_results(result)
    submission, unlocked = progress_service.record_submission(
        current_user, item_type, item, code, safe_result
    )
    return ok(
        submission=submission.to_dict(),
        result=safe_result,
        passed=result.get("passed", 0),
        total=result.get("total", 0),
        completed=result.get("status") == "passed",
        achievements_unlocked=unlocked,
        current_level=current_user.current_level,
    )
