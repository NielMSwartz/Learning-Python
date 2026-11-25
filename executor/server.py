"""HTTP front end for the isolated Python execution service.

This service has no database connection, no access to the web app's environment,
and is the only component allowed to start a Python process with learner code.
"""

from __future__ import annotations

import hmac
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from werkzeug.exceptions import BadRequest

from engine import ValidationError, execute

# Local runs share the web app's .env; Docker passes the same values explicitly.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

EXECUTOR_TOKEN = os.getenv("EXECUTOR_TOKEN", "local-dev-executor-token")
WORKDIR = os.getenv("EXECUTOR_WORKDIR", "/tmp/python-academy-exec")
DEFAULT_CPU = int(os.getenv("EXECUTION_TIMEOUT_SECONDS", "5"))
DEFAULT_MEMORY = int(os.getenv("EXECUTION_MEMORY_MB", "192"))


@app.get("/health")
def health():
    return jsonify(status="ok", service="python-academy-executor")


@app.post("/execute")
def run_code():
    supplied = request.headers.get("X-Executor-Token", "")
    if not hmac.compare_digest(supplied, EXECUTOR_TOKEN):
        return jsonify(error={"code": 401, "message": "Invalid executor token"}), 401

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise BadRequest("A JSON object is required")
    try:
        result = execute(payload, WORKDIR, DEFAULT_CPU, DEFAULT_MEMORY)
    except ValidationError as exc:
        return jsonify(error={"code": 400, "message": str(exc)}), 400
    except Exception:  # never leak internals to the caller
        app.logger.exception("Execution failed")
        return jsonify(error={"code": 500, "message": "Execution service error"}), 500
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("EXECUTOR_PORT", "9000")), threaded=True)
