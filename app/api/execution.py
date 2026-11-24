"""Run arbitrary learner code in the playground / IDE and format Python source."""

from __future__ import annotations

from flask import current_app
from flask_login import current_user

from . import api_bp
from .utils import api_login_required, body, error, ok, require_fields
from ..services.executor_client import ExecutionUnavailable, run_code


@api_bp.post("/execute")
@api_login_required
def execute_code():
    data = body()
    message = require_fields(["code"], data)
    if message:
        return error(message)
    code = str(data["code"])
    if len(code) > 100_000:
        return error("Code is too large")
    files = {"main.py": code}
    extra = data.get("files")
    if isinstance(extra, dict):
        for name, content in list(extra.items())[:24]:
            if isinstance(name, str) and isinstance(content, str) and name.endswith(".py"):
                files[name] = content[:100_000]
    entrypoint = str(data.get("entrypoint", "main.py"))
    if entrypoint not in files:
        return error("Entrypoint file is missing")
    stdin = str(data.get("stdin", ""))[:16_000]
    try:
        result = run_code(files, entrypoint=entrypoint, stdin=stdin)
    except ExecutionUnavailable as exc:
        return error(str(exc), 503)
    return ok(**result)


@api_bp.post("/format")
@api_login_required
def format_code():
    """Format source with Black. Parsing is safe; no learner code is executed."""
    code = str(body().get("code", ""))
    if not code.strip():
        return error("There is no code to format")
    if len(code) > 100_000:
        return error("Code is too large")
    try:
        import black
    except ImportError:
        return error("Code formatting is not installed on this deployment", 501)
    try:
        formatted = black.format_str(
            code,
            mode=black.Mode(line_length=int(current_user.preference("line_length", 88))),
        )
    except Exception as exc:
        return error(f"Cannot format: {exc}")
    return ok(code=formatted)
