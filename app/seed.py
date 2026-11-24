"""Idempotent database seeding from the curriculum modules.

Run with ``flask seed`` (or automatically on first local development boot).
Existing rows are updated in place so curriculum improvements can be deployed
without losing a learner's progress.
"""

from __future__ import annotations

from .curriculum.achievements import ACHIEVEMENTS
from .curriculum.challenges import CHALLENGES
from .curriculum.projects_advanced import PROJECTS as PROJECTS_3
from .curriculum.projects_beginner import PROJECTS as PROJECTS_1
from .curriculum.projects_intermediate import PROJECTS as PROJECTS_2
from .curriculum.projects_professional import PROJECTS as PROJECTS_4
from .curriculum.topics_advanced import TOPICS as TOPICS_3
from .curriculum.topics_beginner import TOPICS as TOPICS_1
from .curriculum.topics_intermediate import TOPICS as TOPICS_2
from .curriculum.topics_professional import TOPICS as TOPICS_4
from .extensions import db
from .models import Achievement, Challenge, Exercise, Project, Topic

LEVELS = {
    1: {
        "name": "Beginner",
        "tagline": "Build the foundations by making small, complete programs.",
        "description": "Variables, data structures, control flow and functions — applied in five projects.",
    },
    2: {
        "name": "Intermediate",
        "tagline": "Structure data and work with the outside world.",
        "description": "Objects, files, JSON, APIs and generators applied to six practical projects.",
    },
    3: {
        "name": "Advanced",
        "tagline": "Build real applications and reason about their behaviour.",
        "description": "Flask, SQL, REST, testing, concurrency and data pipelines.",
    },
    4: {
        "name": "Professional Development",
        "tagline": "Write code you would be happy to maintain for years.",
        "description": "Architecture, patterns, security, deployment and CI/CD.",
    },
}

ALL_TOPICS = TOPICS_1 + TOPICS_2 + TOPICS_3 + TOPICS_4
ALL_PROJECTS = PROJECTS_1 + PROJECTS_2 + PROJECTS_3 + PROJECTS_4


def _upsert(model, slug: str, values: dict):
    row = model.query.filter_by(slug=slug).first()
    if row is None:
        row = model(slug=slug)
        db.session.add(row)
    for key, value in values.items():
        setattr(row, key, value)
    db.session.flush()  # make row.id available for dependent rows
    return row


def seed_all() -> dict[str, int]:
    """Insert or update all curriculum content. Safe to call repeatedly."""
    counts = {"achievements": 0, "topics": 0, "exercises": 0, "projects": 0, "challenges": 0}

    for code, name, description, icon in ACHIEVEMENTS:
        row = Achievement.query.filter_by(code=code).first()
        if row is None:
            row = Achievement(code=code)
            db.session.add(row)
        row.name = name
        row.description = description
        row.icon = icon
        counts["achievements"] += 1

    topic_sets = {1: TOPICS_1, 2: TOPICS_2, 3: TOPICS_3, 4: TOPICS_4}
    for level, topics in topic_sets.items():
        for order, topic in enumerate(topics, start=1):
            row = _upsert(Topic, topic["slug"], dict(
                title=topic["title"], level=level, category=topic["category"],
                summary=topic["summary"], explanation=topic["explanation"],
                examples=topic["examples"], mistakes=topic["mistakes"],
                why_useful=topic["why_useful"], order_index=order,
            ))
            counts["topics"] += 1
            exercise = topic["exercise"]
            ex_slug = f"{topic['slug']}--{exercise['slug']}"
            ex_row = Exercise.query.filter_by(slug=ex_slug).first()
            if ex_row is None:
                ex_row = Exercise(slug=ex_slug)
                db.session.add(ex_row)
            ex_row.topic_id = row.id
            ex_row.prompt = exercise["prompt"]
            ex_row.starter_code = exercise["starter_code"]
            ex_row.tests = exercise["tests"]
            ex_row.order_index = 1
            counts["exercises"] += 1

    for index, project in enumerate(ALL_PROJECTS):
        _upsert(Project, project["slug"], dict(
            title=project["title"], level=project["level"], subtitle=project["subtitle"],
            intro=project["intro"], outcomes=project["outcomes"], concepts=project["concepts"],
            objectives=project["objectives"], steps=project["steps"],
            requirements=project["requirements"], tests=project["tests"],
            starter_code=project["starter_code"], summary=project["summary"],
            estimated_minutes=project["estimated_minutes"], order_index=index + 1,
        ))
        counts["projects"] += 1

    for index, challenge in enumerate(CHALLENGES):
        _upsert(Challenge, challenge["slug"], dict(
            title=challenge["title"], level=challenge["level"], category=challenge["category"],
            difficulty=challenge["difficulty"], description=challenge["description"],
            input_spec=challenge["input_spec"], output_spec=challenge["output_spec"],
            examples=challenge["examples"], hints=challenge["hints"],
            concept_explanation=challenge["concept_explanation"], tests=challenge["tests"],
            starter_code=challenge["starter_code"], points=challenge["points"],
            order_index=index + 1,
        ))
        counts["challenges"] += 1

    db.session.commit()
    return counts


def level_projects(level: int) -> list[Project]:
    return (
        Project.query.filter_by(level=level)
        .order_by(Project.order_index)
        .all()
    )
