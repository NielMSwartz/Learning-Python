"""Progress, unlocking, statistics and achievement rules."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Any

from ..extensions import db
from ..models import (
    Achievement,
    Bookmark,
    Challenge,
    Exercise,
    Progress,
    Project,
    Snippet,
    Submission,
    Topic,
    User,
    UserAchievement,
    utcnow,
)

ITEM_LABELS = {"project": "Project", "challenge": "Challenge", "exercise": "Exercise", "topic": "Lesson"}


def completed_ids(user_id: int, item_type: str) -> set[int]:
    rows = (
        db.session.query(Progress.item_id)
        .filter_by(user_id=user_id, item_type=item_type, status="completed")
        .all()
    )
    return {row[0] for row in rows}


def level_projects(level: int) -> list[Project]:
    return Project.query.filter_by(level=level).order_by(Project.order_index).all()


def level_unlocked(user: User, level: int) -> bool:
    if level <= 1:
        return True
    done = completed_ids(user.id, "project")
    previous = level_projects(level - 1)
    return bool(previous) and all(project.id in done for project in previous)


def project_unlocked(user: User, project: Project) -> bool:
    if not level_unlocked(user, project.level):
        return False
    siblings = level_projects(project.level)
    index = next((i for i, item in enumerate(siblings) if item.id == project.id), 0)
    if index == 0:
        return True
    return siblings[index - 1].id in completed_ids(user.id, "project")


def level_info(user: User) -> list[dict[str, Any]]:
    done = completed_ids(user.id, "project")
    result = []
    for level in range(1, 5):
        projects = level_projects(level)
        result.append({
            "level": level,
            "name": {1: "Beginner", 2: "Intermediate", 3: "Advanced", 4: "Professional"}[level],
            "unlocked": level_unlocked(user, level),
            "project_count": len(projects),
            "completed_count": sum(1 for p in projects if p.id in done),
        })
    return result


def pathway(user: User) -> list[dict[str, Any]]:
    done = completed_ids(user.id, "project")
    result = []
    for level in range(1, 5):
        level_items = level_projects(level)
        projects = []
        for project in level_items:
            progress = Progress.for_item(user.id, "project", project.id)
            projects.append({
                **project.to_dict(),
                "status": progress.status if progress else "not_started",
                "score": progress.score if progress else 0,
                "unlocked": project_unlocked(user, project),
                "completed": project.id in done,
                "last_activity": progress.updated_at.isoformat() if progress else None,
            })
        result.append({
            "level": level,
            "name": {1: "Beginner", 2: "Intermediate", 3: "Advanced", 4: "Professional"}[level],
            "unlocked": level_unlocked(user, level),
            "project_count": len(level_items),
            "completed_count": sum(1 for project in level_items if project.id in done),
            "projects": projects,
            "requirement": f"Complete all projects in Level {level - 1} to unlock" if level > 1 else "Available from the start",
        })
    return result


def _item_summary(user: User, item_type: str, item_id: int) -> dict[str, Any] | None:
    model = {"project": Project, "challenge": Challenge, "exercise": Exercise, "topic": Topic}.get(item_type)
    if model is None:
        return None
    item = db.session.get(model, item_id)
    if item is None:
        return None
    progress = Progress.for_item(user.id, item_type, item_id)
    title = getattr(item, "title", None) or getattr(item, "prompt", "")[:80] or "Practice exercise"
    slug = getattr(item, "slug", str(item_id))
    return {
        "type": item_type,
        "id": item_id,
        "slug": slug,
        "title": title,
        "level": getattr(item, "level", None),
        "status": progress.status if progress else "not_started",
        "score": progress.score if progress else 0,
        "last_code": progress.last_code if progress else "",
        "updated_at": progress.updated_at.isoformat() if progress else None,
    }


def continue_learning(user: User) -> dict[str, Any] | None:
    row = (
        Progress.query.filter(
            Progress.user_id == user.id,
            Progress.status == "in_progress",
            Progress.item_type.in_(["project", "challenge", "exercise"]),
        )
        .order_by(Progress.updated_at.desc())
        .first()
    )
    if row:
        return _item_summary(user, row.item_type, row.item_id)
    row = (
        Progress.query.filter(
            Progress.user_id == user.id,
            Progress.item_type.in_(["project", "challenge", "exercise"]),
        )
        .order_by(Progress.updated_at.desc())
        .first()
    )
    return _item_summary(user, row.item_type, row.item_id) if row else None


def recent_projects(user: User, limit: int = 3) -> list[dict[str, Any]]:
    rows = (
        Progress.query.filter_by(user_id=user.id, item_type="project")
        .order_by(Progress.updated_at.desc())
        .limit(limit)
        .all()
    )
    return [item for item in (_item_summary(user, "project", row.item_id) for row in rows) if item]


def recommended_challenges(user: User, limit: int = 3) -> list[dict[str, Any]]:
    done = completed_ids(user.id, "challenge")
    candidates = [
        challenge for challenge in Challenge.query.filter(Challenge.level <= user.current_level).all()
        if challenge.id not in done
    ]
    candidates.sort(key=lambda c: (abs(c.difficulty - max(1, min(5, user.current_level))), c.order_index))
    return [c.public_dict() for c in candidates[:limit]]


def achievements(user: User) -> list[dict[str, Any]]:
    earned = {row.achievement_id: row.earned_at for row in user.achievements}
    result = []
    for row in Achievement.query.order_by(Achievement.id).all():
        result.append(row.to_dict(earned.get(row.id)))
    return result


def dashboard(user: User) -> dict[str, Any]:
    done_projects = completed_ids(user.id, "project")
    done_challenges = completed_ids(user.id, "challenge")
    done_exercises = completed_ids(user.id, "exercise")
    submissions = Submission.query.filter_by(user_id=user.id).all()
    total_tests = sum(s.total for s in submissions)
    passed_tests = sum(s.passed for s in submissions)
    return {
        "user": user.public_dict(),
        "level": {
            "current": user.current_level,
            "name": {1: "Beginner", 2: "Intermediate", 3: "Advanced", 4: "Professional"}[user.current_level],
            "levels": level_info(user),
        },
        "stats": {
            "projects_completed": len(done_projects),
            "projects_total": Project.query.count(),
            "challenges_completed": len(done_challenges),
            "challenges_total": Challenge.query.count(),
            "exercises_completed": len(done_exercises),
            "coding_hours": round(user.total_coding_seconds / 3600, 1),
            "streak": user.streak,
            "longest_streak": user.longest_streak,
            "success_rate": round(100 * passed_tests / total_tests, 1) if total_tests else 0,
        },
        "continue_learning": continue_learning(user),
        "recent_projects": recent_projects(user),
        "recommended_challenges": recommended_challenges(user),
        "achievements": achievements(user),
        "current_module": {
            "level": user.current_level,
            "name": {1: "Beginner", 2: "Intermediate", 3: "Advanced", 4: "Professional"}[user.current_level],
            "progress": sum(
                1 for p in level_projects(user.current_level) if p.id in done_projects
            ),
            "total": len(level_projects(user.current_level)),
        },
    }


def evaluate_achievements(user: User) -> list[str]:
    done_projects = completed_ids(user.id, "project")
    done_challenges = completed_ids(user.id, "challenge")
    done_exercises = completed_ids(user.id, "exercise")
    perfect = Submission.query.filter_by(user_id=user.id, score=100).count()
    snippets = Snippet.query.filter_by(user_id=user.id).count()
    rules = {
        "first-steps": bool(done_projects or done_challenges or done_exercises),
        "project-novice": len(done_projects) >= 1,
        "project-builder": len(done_projects) >= 5,
        "project-master": len(done_projects) >= 15,
        "challenge-hunter": len(done_challenges) >= 10,
        "perfect-score": perfect >= 5,
        "streak-7": user.streak >= 7,
        "streak-30": user.streak >= 30,
        "code-marathon": user.total_coding_seconds >= 3600,
        "library-reader": len(done_exercises) >= 10,
        "snippet-collector": snippets >= 10,
        "all-levels": user.current_level >= 4,
    }
    unlocked = []
    existing = {row.achievement_id for row in user.achievements}
    for achievement in Achievement.query.all():
        if rules.get(achievement.code) and achievement.id not in existing:
            db.session.add(UserAchievement(user_id=user.id, achievement_id=achievement.id))
            unlocked.append(achievement.code)
    return unlocked


def recompute_level(user: User) -> bool:
    level = 1
    for candidate in range(2, 5):
        previous = level_projects(candidate - 1)
        done = completed_ids(user.id, "project")
        if previous and all(p.id in done for p in previous):
            level = candidate
        else:
            break
    changed = level != user.current_level
    user.current_level = level
    return changed


def record_submission(
    user: User,
    item_type: str,
    item,
    code: str,
    result: dict[str, Any],
) -> tuple[Any, list[str]]:
    """Persist a graded submission and update all derived progress state."""
    from ..models import Submission

    passed = int(result.get("passed", 0))
    total = int(result.get("total", 0))
    score = round(100 * passed / total) if total else 0
    submission = Submission(
        user_id=user.id,
        item_type=item_type,
        item_id=item.id,
        code=code,
        passed=passed,
        total=total,
        score=score,
        results=result.get("results", []),
        error=result.get("error"),
        duration_ms=int(result.get("duration_ms", 0)),
    )
    db.session.add(submission)

    progress = Progress.get_or_create(user.id, item_type, item.id)
    progress.attempts = (progress.attempts or 0) + 1
    progress.last_code = code
    progress.score = max(progress.score or 0, score)
    if score == 100 and total > 0:
        first_completion = progress.status != "completed"
        progress.status = "completed"
        if progress.completed_at is None:
            progress.completed_at = utcnow()
        if first_completion:
            activity = DailyActivityOrCreate(user.id)
            if item_type == "project":
                activity.projects += 1
            elif item_type == "challenge":
                activity.challenges += 1
            elif item_type == "exercise":
                activity.exercises += 1
    else:
        progress.status = "in_progress"

    user.touch()
    recompute_level(user)
    unlocked = evaluate_achievements(user)
    db.session.commit()
    return submission, unlocked


def DailyActivityOrCreate(user_id: int):
    from ..models import DailyActivity

    return DailyActivity.get_or_create(user_id, utcnow().date())


def mark_topic_studied(user: User, topic: Topic) -> list[str]:
    progress = Progress.get_or_create(user.id, "topic", topic.id)
    if progress.status != "completed":
        progress.status = "completed"
        progress.score = 100
        progress.completed_at = utcnow()
        user.touch()
    unlocked = evaluate_achievements(user)
    db.session.commit()
    return unlocked


def stats(user: User) -> dict[str, Any]:
    submissions = Submission.query.filter_by(user_id=user.id).order_by(Submission.created_at.desc()).all()
    total_tests = sum(s.total for s in submissions)
    passed_tests = sum(s.passed for s in submissions)
    categories: dict[str, list[int]] = defaultdict(list)
    challenge_map = {c.id: c for c in Challenge.query.all()}
    for submission in submissions:
        if submission.item_type == "challenge" and submission.item_id in challenge_map:
            categories[challenge_map[submission.item_id].category].append(submission.score)

    def ranked(reverse: bool) -> list[dict[str, Any]]:
        rows = [
            {"category": name, "average": round(sum(scores) / len(scores), 1), "attempts": len(scores)}
            for name, scores in categories.items() if len(scores) >= 2
        ]
        rows.sort(key=lambda row: row["average"], reverse=reverse)
        return rows[:3]

    today = utcnow().date()
    activity_map = {row.date: row for row in user.activity}
    series = []
    for offset in range(29, -1, -1):
        day = today - timedelta(days=offset)
        row = activity_map.get(day)
        series.append({
            "date": day.isoformat(),
            "seconds": row.seconds if row else 0,
            "projects": row.projects if row else 0,
            "exercises": row.exercises if row else 0,
            "challenges": row.challenges if row else 0,
        })

    done_projects = completed_ids(user.id, "project")
    done_challenges = completed_ids(user.id, "challenge")
    done_exercises = completed_ids(user.id, "exercise")
    studied = completed_ids(user.id, "topic")
    next_project = next(
        (p for level in range(1, 5) for p in level_projects(level)
         if p.id not in done_projects and project_unlocked(user, p)),
        None,
    )
    recommendations = []
    if next_project:
        recommendations.append({"type": "project", "title": next_project.title, "slug": next_project.slug,
                                "reason": "Next project in your learning pathway"})
    for challenge in recommended_challenges(user, 2):
        recommendations.append({"type": "challenge", "title": challenge["title"], "slug": challenge["slug"],
                                "reason": "Practice at your current level"})

    return {
        "totals": {
            "projects": len(done_projects),
            "exercises": len(done_exercises),
            "challenges": len(done_challenges),
            "topics_studied": len(studied),
            "coding_hours": round(user.total_coding_seconds / 3600, 1),
            "success_rate": round(100 * passed_tests / total_tests, 1) if total_tests else 0,
            "submissions": len(submissions),
            "current_level": user.current_level,
            "streak": user.streak,
        },
        "weak_areas": ranked(False),
        "strong_areas": ranked(True),
        "activity": series,
        "recommendations": recommendations,
        "level_progress": level_info(user),
        "achievements": achievements(user),
    }
