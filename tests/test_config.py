"""Environment-driven configuration, including Neon PostgreSQL URLs."""

from __future__ import annotations

import config as config_module


def test_neon_style_urls_use_psycopg_driver(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@ep-test.neon.tech/academy?sslmode=require")
    assert config_module.Config.database_uri().startswith("postgresql+psycopg://")

    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@ep-test.neon.tech/academy?sslmode=require")
    uri = config_module.Config.database_uri()
    assert uri.startswith("postgresql+psycopg://")
    assert "sslmode=require" in uri


def test_sqlite_fallback_uses_instance_directory(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SQLITE_PATH", "fallback.db")
    assert config_module.Config.database_uri().endswith(r"instance\fallback.db")
