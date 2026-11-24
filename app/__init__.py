"""Application factory for Python Academy."""

from __future__ import annotations

import logging
import secrets
from datetime import datetime, timezone

from flask import Flask, abort, g, jsonify, render_template, request, session
from werkzeug.exceptions import HTTPException

from config import CONFIGS

from .extensions import db, login_manager, migrate
from .models import User


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    config = CONFIGS[config_name or __import__("os").getenv("FLASK_CONFIG", "default")]
    config.init_app(app)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    # ---------------------------------------------------------------- CSRF ---
    unsafe_methods = {"POST", "PUT", "PATCH", "DELETE"}

    def new_csrf_token() -> str:
        # Return the existing token so every place on a page (meta tag, forms,
        # JavaScript) sends the same value.
        token = session.get("csrf_token")
        if not token:
            token = secrets.token_urlsafe(32)
            session["csrf_token"] = token
        return token

    app.jinja_env.globals["csrf_token"] = new_csrf_token

    @app.before_request
    def csrf_protect():
        g.start_time = datetime.now(timezone.utc)
        if app.config.get("TESTING") or request.method not in unsafe_methods:
            return
        if request.path == "/health":
            return
        supplied = (
            request.headers.get("X-CSRF-Token")
            or request.form.get("csrf_token")
            or (request.get_json(silent=True) or {}).get("csrf_token")
        )
        expected = session.get("csrf_token")
        if not expected or not supplied or not secrets.compare_digest(str(supplied), str(expected)):
            abort(403, description="Your session expired or the CSRF token is invalid. Please reload the page.")

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        if request.is_secure:
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response

    # --------------------------------------------------------------- errors ---
    def wants_json() -> bool:
        return request.path.startswith("/api/") or "application/json" in request.headers.get("Accept", "")

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        if wants_json():
            return jsonify(error={"code": error.code, "message": error.description}), error.code
        return render_template("error.html", error=error), error.code

    @app.errorhandler(Exception)
    def handle_unexpected(error: Exception):
        app.logger.exception("Unhandled error: %s", error)
        if wants_json():
            return jsonify(error={"code": 500, "message": "An unexpected server error occurred."}), 500
        return render_template("error.html", error=type("Error", (), {"code": 500, "description": "Something went wrong."})()), 500

    # ------------------------------------------------------------- filters ---
    @app.template_filter("duration")
    def duration_filter(seconds: int | None) -> str:
        seconds = int(seconds or 0)
        hours, rest = divmod(seconds, 3600)
        minutes = rest // 60
        return f"{hours}h {minutes}m" if hours else f"{minutes}m"

    @app.template_filter("level_name")
    def level_name_filter(level: int) -> str:
        return {1: "Beginner", 2: "Intermediate", 3: "Advanced", 4: "Professional"}.get(int(level), "Unknown")

    @app.get("/health")
    def health():
        return jsonify(status="ok", service="python-academy-web")

    # ------------------------------------------------------------ blueprints --
    from .api import api_bp
    from .web import web_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)
    register_cli(app)

    if app.config.get("TESTING"):
        with app.app_context():
            db.create_all()
    else:
        # First-run bootstrap for local development. Neon deployments should run
        # `flask db upgrade && flask seed` explicitly (see README).
        uri = str(app.config.get("SQLALCHEMY_DATABASE_URI", ""))
        if uri.startswith("sqlite:") and not app.config.get("DISABLE_AUTO_SETUP"):
            with app.app_context():
                db.create_all()
                try:
                    from .seed import seed_all

                    seed_all()
                except Exception:  # pragma: no cover - logged, never breaks boot
                    app.logger.exception("First-run seeding failed")

    logging.getLogger("python_academy").setLevel(logging.INFO)
    return app


def register_cli(app: Flask) -> None:
    @app.cli.command("seed")
    def seed_command() -> None:
        """Populate the database with the learning pathway (idempotent)."""
        from .seed import seed_all

        counts = seed_all()
        print("Seeded:", counts)

    @app.cli.command("create-user")
    def create_user_command() -> None:
        """Create a user interactively: flask create-user"""
        from getpass import getpass

        from . import db
        from .models import User

        username = input("Username: ").strip()
        email = input("Email: ").strip()
        password = getpass("Password: ")
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            raise SystemExit("That username or email is already registered.")
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"Created user {username} (id={user.id})")
