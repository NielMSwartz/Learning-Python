"""Client for the isolated code execution service.

The web process never imports learner code. It only speaks HTTP to the sandbox,
using a shared secret and a short timeout.
"""

from __future__ import annotations

from typing import Any

import requests
from flask import current_app


class ExecutionUnavailable(RuntimeError):
    """Raised when the sandbox cannot be reached or rejects the request."""


def _post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    url = f"{current_app.config['EXECUTOR_URL']}{path}"
    timeout = int(current_app.config.get("EXECUTION_TIMEOUT_SECONDS", 5))
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"X-Executor-Token": current_app.config["EXECUTOR_TOKEN"]},
            timeout=(3, timeout + 15),
        )
    except requests.RequestException as exc:
        current_app.logger.warning("Executor unavailable: %s", exc)
        raise ExecutionUnavailable(
            "Code execution is temporarily unavailable. Check that the executor service is running, "
            "then try again."
        ) from exc

    if response.status_code == 401:
        raise ExecutionUnavailable("The execution service rejected this application's credentials.")
    if response.status_code >= 400:
        body = response.json().get("error", {}) if response.is_json else {}
        raise ExecutionUnavailable(body.get("message", "The execution service rejected the request."))
    return response.json()


def run_code(files: dict[str, str], entrypoint: str = "main.py", stdin: str = "") -> dict[str, Any]:
    return _post("/execute", {
        "mode": "run",
        "files": files,
        "entrypoint": entrypoint,
        "stdin": stdin,
        "timeout_seconds": current_app.config.get("EXECUTION_TIMEOUT_SECONDS", 5),
        "memory_mb": current_app.config.get("EXECUTION_MEMORY_MB", 192),
    })


def grade(files: dict[str, str], tests: list[dict[str, Any]], entrypoint: str = "main.py") -> dict[str, Any]:
    return _post("/execute", {
        "mode": "test",
        "files": files,
        "entrypoint": entrypoint,
        "tests": tests,
        "timeout_seconds": current_app.config.get("EXECUTION_TIMEOUT_SECONDS", 5),
        "memory_mb": current_app.config.get("EXECUTION_MEMORY_MB", 192),
    })
