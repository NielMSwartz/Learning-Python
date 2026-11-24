"""Browser pages. All data is loaded by the authenticated JSON API."""

from __future__ import annotations

from flask import abort, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required, logout_user

from ..extensions import db
from ..models import Challenge, Exercise, PasswordResetToken, Project, Topic
from . import web_bp


@web_bp.app_context_processor
def inject_globals():
    return {"level_name": lambda level: {
        1: "Beginner", 2: "Intermediate", 3: "Advanced", 4: "Professional"
    }.get(int(level or 1), "Beginner")}


@web_bp.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html", title="Dashboard")


@web_bp.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("web.dashboard"))
    return render_template("auth/login.html", title="Sign in")


@web_bp.route("/register")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("web.dashboard"))
    return render_template("auth/register.html", title="Create account")


@web_bp.route("/forgot")
def forgot():
    return render_template("auth/forgot.html", title="Reset password")


@web_bp.route("/reset/<token>")
def reset(token: str):
    row = PasswordResetToken.find_valid(token)
    if row is None:
        return render_template("auth/reset.html", title="Reset password", token=None)
    return render_template("auth/reset.html", title="Reset password", token=token)


@web_bp.post("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("web.login"))


@web_bp.route("/learn")
@login_required
def learn():
    return render_template("learn.html", title="Learning pathway")


@web_bp.route("/learn/project/<slug>")
@login_required
def project(slug: str):
    project = Project.query.filter_by(slug=slug).first_or_404()
    return render_template("workspace.html", title=project.title,
                           item_type="project", item_slug=slug, item_title=project.title,
                           item_level=project.level)


@web_bp.route("/practice/<slug>")
@login_required
def exercise(slug: str):
    exercise = Exercise.query.filter_by(slug=slug).first_or_404()
    return render_template("workspace.html", title="Practice",
                           item_type="exercise", item_slug=slug,
                           item_title=exercise.topic.title, item_level=exercise.topic.level)


@web_bp.route("/library")
@login_required
def library():
    return render_template("library.html", title="Knowledge library")


@web_bp.route("/library/<slug>")
@login_required
def topic(slug: str):
    topic = Topic.query.filter_by(slug=slug).first_or_404()
    return render_template("topic.html", title=topic.title, topic_slug=slug)


@web_bp.route("/challenges")
@login_required
def challenges():
    return render_template("challenges.html", title="Coding challenges")


@web_bp.route("/challenges/<slug>")
@login_required
def challenge(slug: str):
    challenge = Challenge.query.filter_by(slug=slug).first_or_404()
    return render_template("workspace.html", title=challenge.title,
                           item_type="challenge", item_slug=slug,
                           item_title=challenge.title, item_level=challenge.level)


@web_bp.route("/playground")
@login_required
def playground():
    return render_template("playground.html", title="Playground")


@web_bp.route("/ide")
@login_required
def ide():
    return render_template("ide.html", title="IDE")


@web_bp.route("/snippets")
@login_required
def snippets():
    return render_template("snippets.html", title="Snippets")


@web_bp.route("/stats")
@login_required
def stats():
    return render_template("stats.html", title="My progress")


@web_bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html", title="Settings")


@web_bp.route("/manifest.webmanifest")
def manifest():
    response = send_from_directory("static", "manifest.webmanifest")
    response.headers["Content-Type"] = "application/manifest+json"
    return response


@web_bp.route("/sw.js")
def service_worker():
    response = send_from_directory("static", "sw.js")
    response.headers["Content-Type"] = "application/javascript"
    response.headers["Cache-Control"] = "no-cache"
    return response


@web_bp.route("/offline")
def offline():
    return render_template("offline.html", title="Offline")
