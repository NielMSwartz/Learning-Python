"""Execution engine tests: real Python subprocesses, limits and isolation."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "executor"))

from engine import ValidationError, execute, validate_files  # noqa: E402


def run(files: dict[str, str], root: Path, **kwargs) -> dict:
    payload = {"mode": "run", "files": files, "entrypoint": "main.py", **kwargs}
    return execute(payload, str(root), 2, 192)


def test_run_stdout_and_stdin(tmp_path):
    result = run({
        "main.py": "name = input()\nprint(f'Hello {name}')"
    }, tmp_path, stdin="Ada\n")
    assert result["status"] == "ok"
    assert result["stdout"].strip() == "Hello Ada"


def test_multi_file_project(tmp_path):
    result = run({
        "main.py": "from helpers import double\nprint(double(21))",
        "helpers.py": "def double(value):\n    return value * 2\n",
    }, tmp_path)
    assert result["status"] == "ok"
    assert result["stdout"].strip() == "42"


def test_runtime_errors_are_returned_without_runner_internals(tmp_path):
    result = run({"main.py": "print('before')\nraise ValueError('learner mistake')"}, tmp_path)
    assert result["status"] == "error"
    assert "ValueError: learner mistake" in result["error"]
    assert "sandbox_runner.py" not in result["error"]
    assert "main.py" in result["error"]


def test_timeout_is_enforced(tmp_path):
    result = run({"main.py": "while True:\n    pass"}, tmp_path, timeout_seconds=1)
    assert result["status"] == "error"
    assert result.get("timed_out") is True
    assert "timed out" in result["error"]


def test_output_is_capped(tmp_path):
    result = run({"main.py": "print('x' * 200000)"}, tmp_path)
    assert result["truncated"] is True
    assert len(result["stdout"]) <= 65_536


def test_environment_is_not_leaked(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://secret")
    monkeypatch.setenv("SECRET_KEY", "secret-value")
    result = run({
        "main.py": "import os\nprint(os.getenv('DATABASE_URL'))\nprint(os.getenv('SECRET_KEY'))"
    }, tmp_path)
    assert result["stdout"].split() == ["None", "None"]


def test_network_primitives_are_blocked(tmp_path):
    result = run({"main.py": """
import socket
try:
    socket.create_connection(('127.0.0.1', 9), 0.2)
    print('allowed')
except PermissionError:
    print('blocked')
"""}, tmp_path)
    assert result["status"] == "ok"
    assert result["stdout"].strip() == "blocked"


def test_assertion_grading_and_hidden_flag(tmp_path):
    result = execute({
        "mode": "test",
        "files": {"main.py": "def add(a, b):\n    return a + b\n"},
        "tests": [
            {"name": "Public", "assertion": "assert solution.add(2, 3) == 5"},
            {"name": "Hidden", "hidden": True, "assertion": "assert solution.add(10, 1) == 11"},
        ],
    }, str(tmp_path), 2, 192)
    assert result["status"] == "passed"
    assert result["passed"] == 2
    assert result["results"][1]["hidden"] is True


def test_failing_assertion_reports_learner_error(tmp_path):
    result = execute({
        "mode": "test",
        "files": {"main.py": "def add(a, b):\n    return a - b\n"},
        "tests": [{"name": "Sum", "assertion": "assert solution.add(2, 3) == 5"}],
    }, str(tmp_path), 2, 192)
    assert result["status"] == "failed"
    assert "AssertionError" in result["results"][0]["error"]


def test_path_traversal_and_oversized_input_rejected():
    with pytest.raises(ValidationError):
        validate_files({"../escape.py": "print(1)"})
    with pytest.raises(ValidationError):
        validate_files({"main.exe": "print(1)"})
    with pytest.raises(ValidationError):
        validate_files({"main.py": "x" * 200_000})


def test_workspace_is_cleaned_up(tmp_path):
    before = set(tmp_path.iterdir())
    run({"main.py": "open('data.txt', 'w').write('temporary')"}, tmp_path)
    assert set(tmp_path.iterdir()) == before
