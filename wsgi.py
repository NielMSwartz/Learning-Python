"""Gunicorn/WSGI entry point for Python Academy."""

from app import create_app

app = create_app()
