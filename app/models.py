"""Database models for Python Academy.

Every piece of user owned data is scoped with a ``user_id`` foreign key so that
additional users can be supported without changing the schema.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from flask_login import UserMixin
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True, index=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    last_active_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Learning state
    current_level = db.Column(db.Integer, nullable=False, default=1)
    streak = db.Column(db.Integer, nullable=False, default=0)
    longest_streak = db.Column(db.Integer, nullable=False, default=0)
    total_coding_seconds = db.Column(db.Integer, nullable=False, default=0)

    # Preferences (explicit fields are mirrored into this JSON for API convenience)
    theme = db.Column(db.String(10), nullable=False, default="dark")
    preferences = db.Column(db.JSON, nullable=False, default=dict)

    progress = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="user", cascade="all, delete-orphan")
    snippets = relationship("Snippet", back_populates="user", cascade="all, delete-orphan")
    ide_projects = relationship("IDEProject", back_populates="user", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    activity = relationship("DailyActivity", back_populates="user", cascade="all, delete-orphan")
    reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password, method="scrypt")

    def check_password(self, password: str) -> bool:
        try:
            return check_password_hash(self.password_hash, password)
        except (ValueError, TypeError):
            return False

    def touch(self) -> None:
        """Update the daily activity/streak when the user does something meaningful."""
        now = utcnow()
        today = now.date()
        last = self.last_active_at.date() if self.last_active_at else None
        if last != today:
            if last == today - timedelta(days=1):
                self.streak = (self.streak or 0) + 1
            else:
                self.streak = 1
            self.longest_streak = max(self.longest_streak, self.streak)
            self.last_active_at = now
            activity = DailyActivity.get_or_create(self.id, today)
            activity.active = True

    def add_coding_time(self, seconds: int) -> None:
        if seconds <= 0:
            return
        seconds = min(int(seconds), 3600)
        self.total_coding_seconds = (self.total_coding_seconds or 0) + seconds
        activity = DailyActivity.get_or_create(self.id, utcnow().date())
        activity.seconds += seconds
        self.touch()

    def preference(self, key: str, default: Any = None) -> Any:
        prefs = dict(self.preferences or {})
        if hasattr(self, key):
            return getattr(self, key)
        return prefs.get(key, default)

    def apply_preferences(self, values: dict[str, Any]) -> None:
        allowed = {
            "theme": {"dark", "light"},
            "font_size": range(10, 25),
            "tab_size": {2, 4, 8},
            "auto_hint": {True, False},
            "line_wrapping": {True, False},
        }
        prefs = dict(self.preferences or {})
        for key, value in values.items():
            if key not in allowed or value not in allowed[key]:
                continue
            if key == "theme":
                self.theme = value
            elif key in {"font_size", "tab_size"}:
                prefs[key] = int(value)
            else:
                prefs[key] = bool(value)
        self.preferences = prefs

    def public_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "current_level": self.current_level,
            "streak": self.streak,
            "longest_streak": self.longest_streak,
            "total_coding_seconds": self.total_coding_seconds,
            "theme": self.theme,
            "preferences": {
                "font_size": (self.preferences or {}).get("font_size", 14),
                "tab_size": (self.preferences or {}).get("tab_size", 4),
                "auto_hint": (self.preferences or {}).get("auto_hint", True),
                "line_wrapping": (self.preferences or {}).get("line_wrapping", False),
            },
        }


class Topic(db.Model):
    """An entry in the Python knowledge library (also used as a 'lesson')."""

    __tablename__ = "topics"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), nullable=False, unique=True, index=True)
    title = db.Column(db.String(160), nullable=False)
    level = db.Column(db.Integer, nullable=False, index=True)
    category = db.Column(db.String(80), nullable=False, index=True)
    summary = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    examples = db.Column(db.JSON, nullable=False, default=list)
    mistakes = db.Column(db.JSON, nullable=False, default=list)
    why_useful = db.Column(db.Text, nullable=False)
    order_index = db.Column(db.Integer, nullable=False, default=0)

    exercises = relationship("Exercise", back_populates="topic", cascade="all, delete-orphan")

    def to_dict(self, detailed: bool = False) -> dict[str, Any]:
        data = {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "level": self.level,
            "category": self.category,
            "summary": self.summary,
            "order": self.order_index,
        }
        if detailed:
            data.update(
                explanation=self.explanation,
                examples=self.examples or [],
                mistakes=self.mistakes or [],
                why_useful=self.why_useful,
                exercises=[e.to_dict() for e in sorted(self.exercises, key=lambda e: e.order_index)],
            )
        return data


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    slug = db.Column(db.String(160), nullable=False, unique=True, index=True)
    prompt = db.Column(db.Text, nullable=False)
    starter_code = db.Column(db.Text, nullable=False, default="")
    tests = db.Column(db.JSON, nullable=False, default=list)
    order_index = db.Column(db.Integer, nullable=False, default=0)

    topic = relationship("Topic", back_populates="exercises")

    def to_dict(self, include_tests: bool = False) -> dict[str, Any]:
        data = {
            "id": self.id,
            "slug": self.slug,
            "topic_id": self.topic_id,
            "prompt": self.prompt,
            "starter_code": self.starter_code,
            "order": self.order_index,
        }
        if include_tests:
            data["tests"] = self.tests or []
        return data


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), nullable=False, unique=True, index=True)
    title = db.Column(db.String(160), nullable=False)
    level = db.Column(db.Integer, nullable=False, index=True)
    subtitle = db.Column(db.String(255), nullable=False, default="")
    intro = db.Column(db.Text, nullable=False)
    outcomes = db.Column(db.JSON, nullable=False, default=list)
    concepts = db.Column(db.JSON, nullable=False, default=list)
    objectives = db.Column(db.JSON, nullable=False, default=list)
    steps = db.Column(db.JSON, nullable=False, default=list)  # {title, detail, hint}
    requirements = db.Column(db.JSON, nullable=False, default=list)
    tests = db.Column(db.JSON, nullable=False, default=list)  # trusted, never sent verbatim to the browser
    starter_code = db.Column(db.Text, nullable=False, default="")
    summary = db.Column(db.Text, nullable=False, default="")
    estimated_minutes = db.Column(db.Integer, nullable=False, default=60)
    order_index = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self, detailed: bool = False) -> dict[str, Any]:
        data = {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "level": self.level,
            "subtitle": self.subtitle,
            "summary": self.summary,
            "order": self.order_index,
            "estimated_minutes": self.estimated_minutes,
        }
        if detailed:
            data.update(
                intro=self.intro,
                outcomes=self.outcomes or [],
                concepts=self.concepts or [],
                objectives=self.objectives or [],
                steps=self.steps or [],
                requirements=self.requirements or [],
                starter_code=self.starter_code,
                completion_summary=self.summary,
            )
        return data


class Challenge(db.Model):
    __tablename__ = "challenges"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), nullable=False, unique=True, index=True)
    title = db.Column(db.String(160), nullable=False)
    level = db.Column(db.Integer, nullable=False, index=True)
    category = db.Column(db.String(80), nullable=False, index=True)
    difficulty = db.Column(db.Integer, nullable=False, default=1)  # 1-5
    description = db.Column(db.Text, nullable=False)
    input_spec = db.Column(db.Text, nullable=False)
    output_spec = db.Column(db.Text, nullable=False)
    examples = db.Column(db.JSON, nullable=False, default=list)  # {input, output}
    hints = db.Column(db.JSON, nullable=False, default=list)
    concept_explanation = db.Column(db.Text, nullable=False)
    tests = db.Column(db.JSON, nullable=False, default=list)  # includes hidden tests
    starter_code = db.Column(db.Text, nullable=False, default="")
    points = db.Column(db.Integer, nullable=False, default=10)
    order_index = db.Column(db.Integer, nullable=False, default=0)

    def public_dict(self, detailed: bool = False) -> dict[str, Any]:
        data = {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "level": self.level,
            "category": self.category,
            "difficulty": self.difficulty,
            "points": self.points,
            "description": self.description if detailed else self.description[:180],
        }
        if detailed:
            data.update(
                input_spec=self.input_spec,
                output_spec=self.output_spec,
                examples=self.examples or [],
                hints=self.hints or [],
                concept_explanation=self.concept_explanation,
                starter_code=self.starter_code,
            )
        return data


class Progress(db.Model):
    """One row per (user, learning item) with the latest state."""

    __tablename__ = "progress"
    __table_args__ = (UniqueConstraint("user_id", "item_type", "item_id", name="uq_progress_item"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    item_type = db.Column(db.String(20), nullable=False)  # project | challenge | exercise | topic
    item_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="in_progress")
    score = db.Column(db.Integer, nullable=False, default=0)  # percentage of passed tests
    attempts = db.Column(db.Integer, nullable=False, default=0)
    started_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    last_code = db.Column(db.Text, nullable=False, default="")

    user = relationship("User", back_populates="progress")

    @classmethod
    def for_item(cls, user_id: int, item_type: str, item_id: int) -> "Progress | None":
        return cls.query.filter_by(user_id=user_id, item_type=item_type, item_id=item_id).first()

    @classmethod
    def get_or_create(cls, user_id: int, item_type: str, item_id: int) -> "Progress":
        obj = cls.for_item(user_id, item_type, item_id)
        if obj is None:
            obj = cls(user_id=user_id, item_type=item_type, item_id=item_id)
            db.session.add(obj)
        return obj


class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    item_type = db.Column(db.String(20), nullable=False)
    item_id = db.Column(db.Integer, nullable=False)
    code = db.Column(db.Text, nullable=False)
    passed = db.Column(db.Integer, nullable=False, default=0)
    total = db.Column(db.Integer, nullable=False, default=0)
    score = db.Column(db.Integer, nullable=False, default=0)
    results = db.Column(db.JSON, nullable=False, default=list)
    error = db.Column(db.Text, nullable=True)
    duration_ms = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)

    user = relationship("User", back_populates="submissions")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "item_type": self.item_type,
            "item_id": self.item_id,
            "passed": self.passed,
            "total": self.total,
            "score": self.score,
            "results": self.results or [],
            "error": self.error,
            "duration_ms": self.duration_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Snippet(db.Model):
    __tablename__ = "snippets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    code = db.Column(db.Text, nullable=False, default="")
    category = db.Column(db.String(80), nullable=False, default="General")
    tags = db.Column(db.JSON, nullable=False, default=list)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="snippets")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "code": self.code,
            "category": self.category,
            "tags": self.tags or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class IDEProject(db.Model):
    __tablename__ = "ide_projects"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(160), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="ide_projects")
    files = relationship("IDEFile", back_populates="project", cascade="all, delete-orphan")

    def to_dict(self, include_files: bool = False) -> dict[str, Any]:
        data = {
            "id": self.id,
            "name": self.name,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_files:
            data["files"] = [f.to_dict() for f in sorted(self.files, key=lambda f: f.path)]
        return data


class IDEFile(db.Model):
    __tablename__ = "ide_files"
    __table_args__ = (UniqueConstraint("project_id", "path", name="uq_ide_file_path"),)

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("ide_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    path = db.Column(db.String(255), nullable=False)  # e.g. utils/helpers.py
    content = db.Column(db.Text, nullable=False, default="")
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    project = relationship("IDEProject", back_populates="files")

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "path": self.path, "content": self.content}


class Bookmark(db.Model):
    __tablename__ = "bookmarks"
    __table_args__ = (UniqueConstraint("user_id", "topic_id", name="uq_bookmark"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    user = relationship("User", back_populates="bookmarks")
    topic = relationship("Topic")


class Achievement(db.Model):
    __tablename__ = "achievements"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(80), nullable=False, unique=True)
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(40), nullable=False, default="★")

    def to_dict(self, earned_at=None) -> dict[str, Any]:
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "earned_at": earned_at.isoformat() if earned_at else None,
        }


class UserAchievement(db.Model):
    __tablename__ = "user_achievements"
    __table_args__ = (UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    achievement_id = db.Column(db.Integer, db.ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    earned_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement")


class DailyActivity(db.Model):
    __tablename__ = "daily_activity"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_activity_day"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)
    seconds = db.Column(db.Integer, nullable=False, default=0)
    projects = db.Column(db.Integer, nullable=False, default=0)
    exercises = db.Column(db.Integer, nullable=False, default=0)
    challenges = db.Column(db.Integer, nullable=False, default=0)
    active = db.Column(db.Boolean, nullable=False, default=False)

    user = relationship("User", back_populates="activity")

    @classmethod
    def get_or_create(cls, user_id: int, day) -> "DailyActivity":
        row = cls.query.filter_by(user_id=user_id, date=day).first()
        if row is None:
            # Explicit values are important: SQLite does not populate Python-side
            # column defaults until after the next flush.
            row = cls(user_id=user_id, date=day, seconds=0, projects=0,
                      exercises=0, challenges=0, active=False)
            db.session.add(row)
        return row


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = db.Column(db.String(64), nullable=False, unique=True, index=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    used_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    user = relationship("User", back_populates="reset_tokens")

    @classmethod
    def create(cls, user: "User") -> str:
        token = secrets.token_urlsafe(32)
        row = cls(
            user_id=user.id,
            token_hash=token_hash(token),
            expires_at=utcnow() + timedelta(minutes=30),
        )
        db.session.add(row)
        return token

    @classmethod
    def find_valid(cls, token: str) -> "PasswordResetToken | None":
        row = cls.query.filter_by(token_hash=token_hash(token), used_at=None).first()
        if row is None:
            return None
        expires_at = row.expires_at
        # SQLite drops timezone information; treat stored naive UTC as UTC.
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < utcnow():
            return None
        return row
