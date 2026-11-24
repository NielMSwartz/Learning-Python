"""Multi-file IDE project and file storage endpoints (strictly per user)."""

from __future__ import annotations

import re

from flask import request
from flask_login import current_user

from ..extensions import db
from ..models import IDEFile, IDEProject
from . import api_bp
from .utils import api_login_required, body, error, ok

SAFE_PATH = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_./\- ]{0,198}$")
SUFFIXES = {".py", ".json", ".txt", ".csv", ".md"}


def safe_path(raw) -> str | None:
    if not isinstance(raw, str):
        return None
    path = raw.replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    if (
        not path
        or path.startswith("/")
        or ".." in path.split("/")
        or not SAFE_PATH.match(path)
        or "." not in path.rsplit("/", 1)[-1]
        or ("." + path.rsplit(".", 1)[-1].lower()) not in SUFFIXES
    ):
        return None
    return path


def own_project(project_id: int) -> IDEProject | None:
    return IDEProject.query.filter_by(id=project_id, user_id=current_user.id).first()


def own_file(file_id: int) -> IDEFile | None:
    return (
        IDEFile.query.join(IDEProject)
        .filter(IDEFile.id == file_id, IDEProject.user_id == current_user.id)
        .first()
    )


@api_bp.get("/ide/projects")
@api_login_required
def list_projects():
    projects = (
        IDEProject.query.filter_by(user_id=current_user.id)
        .order_by(IDEProject.updated_at.desc())
        .all()
    )
    return ok(projects=[p.to_dict() for p in projects])


@api_bp.post("/ide/projects")
@api_login_required
def create_project():
    name = str(body().get("name", "")).strip()[:160]
    if not name:
        return error("Project name is required")
    project = IDEProject(user_id=current_user.id, name=name)
    project.files.append(IDEFile(path="main.py", content="# Start coding here\n"))
    db.session.add(project)
    db.session.commit()
    return ok(project=project.to_dict(include_files=True))


@api_bp.get("/ide/projects/<int:project_id>")
@api_login_required
def get_project(project_id: int):
    project = own_project(project_id)
    if project is None:
        return error("Project not found", 404)
    return ok(project=project.to_dict(include_files=True))


@api_bp.patch("/ide/projects/<int:project_id>")
@api_login_required
def rename_project(project_id: int):
    project = own_project(project_id)
    if project is None:
        return error("Project not found", 404)
    name = str(body().get("name", "")).strip()[:160]
    if not name:
        return error("Project name is required")
    project.name = name
    db.session.commit()
    return ok(project=project.to_dict())


@api_bp.delete("/ide/projects/<int:project_id>")
@api_login_required
def delete_project(project_id: int):
    project = own_project(project_id)
    if project is None:
        return error("Project not found", 404)
    db.session.delete(project)
    db.session.commit()
    return ok(message="Project deleted")


@api_bp.post("/ide/projects/<int:project_id>/files")
@api_login_required
def create_file(project_id: int):
    project = own_project(project_id)
    if project is None:
        return error("Project not found", 404)
    path = safe_path(body().get("path"))
    if path is None:
        return error("Use a relative path such as utils/helpers.py")
    if any(f.path == path for f in project.files):
        return error("A file with that path already exists", 409)
    if len(project.files) >= 25:
        return error("This project already has the maximum of 25 files")
    file = IDEFile(project_id=project.id, path=path, content=str(body().get("content", ""))[:100_000])
    db.session.add(file)
    db.session.commit()
    return ok(file=file.to_dict())


@api_bp.put("/ide/files/<int:file_id>")
@api_login_required
def save_file(file_id: int):
    file = own_file(file_id)
    if file is None:
        return error("File not found", 404)
    data = body()
    if "content" in data:
        file.content = str(data["content"])[:100_000]
    if "path" in data:
        path = safe_path(data["path"])
        if path is None:
            return error("Invalid file path")
        if any(f.path == path and f.id != file.id for f in file.project.files):
            return error("A file with that path already exists", 409)
        file.path = path
    db.session.commit()
    return ok(file=file.to_dict())


@api_bp.delete("/ide/files/<int:file_id>")
@api_login_required
def delete_file(file_id: int):
    file = own_file(file_id)
    if file is None:
        return error("File not found", 404)
    if len(file.project.files) <= 1:
        return error("A project needs at least one file")
    db.session.delete(file)
    db.session.commit()
    return ok(message="File deleted")


@api_bp.post("/ide/projects/<int:project_id>/save")
@api_login_required
def save_project(project_id: int):
    """Persist the open editor's complete file map in one operation."""
    project = own_project(project_id)
    if project is None:
        return error("Project not found", 404)
    files = body().get("files")
    if not isinstance(files, dict) or not files:
        return error("No files were supplied")
    cleaned: dict[str, str] = {}
    for name, content in files.items():
        path = safe_path(name)
        if path is None or not isinstance(content, str):
            return error("One or more files have an invalid name")
        cleaned[path] = content[:100_000]
    if len(cleaned) > 25:
        return error("Too many files")
    existing = {f.path: f for f in project.files}
    for path, content in cleaned.items():
        if path in existing:
            existing[path].content = content
        else:
            project.files.append(IDEFile(path=path, content=content))
    for path, file in existing.items():
        if path not in cleaned:
            db.session.delete(file)
    db.session.commit()
    return ok(project=project.to_dict(include_files=True))
