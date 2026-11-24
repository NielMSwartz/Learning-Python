"""Configuration for the Python Academy web application.

All deployment specific settings come from environment variables (see .env.example).
The application falls back to a local SQLite database for first-run development so
that the UI can be explored before Neon credentials are configured.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-insecure-secret-change-me")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB per API request

    # Session cookies are safe, same-site and only sent over HTTPS in production.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _bool("SESSION_COOKIE_SECURE")

    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}

    EXECUTOR_URL = os.getenv("EXECUTOR_URL", "http://127.0.0.1:9000").rstrip("/")
    EXECUTOR_TOKEN = os.getenv("EXECUTOR_TOKEN", "local-dev-executor-token")
    EXECUTION_TIMEOUT_SECONDS = int(os.getenv("EXECUTION_TIMEOUT_SECONDS", "5"))
    EXECUTION_MEMORY_MB = int(os.getenv("EXECUTION_MEMORY_MB", "192"))

    MAIL_SERVER = os.getenv("MAIL_SERVER", "")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = _bool("MAIL_USE_TLS", True)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "Python Academy <noreply@example.com>")
    PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")

    RESET_TOKEN_MINUTES = 30
    # Used by deployment commands that manage the schema explicitly (flask db upgrade).
    DISABLE_AUTO_SETUP = _bool("DISABLE_AUTO_SETUP")

    @staticmethod
    def database_uri() -> str:
        url = os.getenv("DATABASE_URL", "").strip()
        if url:
            # SQLAlchemy 2.x uses the psycopg 3 driver by default for postgresql:// URLs.
            if url.startswith("postgres://"):
                url = "postgresql+psycopg://" + url[len("postgres://") :]
            elif url.startswith("postgresql://") and "+psycopg" not in url:
                url = url.replace("postgresql://", "postgresql+psycopg://", 1)
            return url
        path = BASE_DIR / "instance" / os.getenv("SQLITE_PATH", "python_academy.db")
        path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{path}"

    @classmethod
    def init_app(cls, app) -> None:
        app.config["SQLALCHEMY_DATABASE_URI"] = cls.database_uri()


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = False
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "testing-secret-key"
    EXECUTOR_URL = "http://executor.invalid"
    MAIL_SERVER = ""

    @classmethod
    def init_app(cls, app) -> None:
        # Tests always use an isolated in-memory database, never DATABASE_URL.
        app.config["SQLALCHEMY_DATABASE_URI"] = cls.SQLALCHEMY_DATABASE_URI


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = _bool("SESSION_COOKIE_SECURE", True)
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE


CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig if _bool("DEBUG") else Config,
}
