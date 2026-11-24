"""Execution engine: validates input, prepares an isolated workspace and runs code."""

from __future__ import annotations

import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

RUNNER = Path(__file__).with_name("sandbox_runner.py")
MAX_FILES = 25
MAX_FILE_BYTES = 100_000
MAX_TOTAL_BYTES = 500_000
MAX_STDIN_BYTES = 16_000
MAX_TESTS = 16
PAYLOAD_RE_TEMPLATE = r"\n__PAYLOAD_{nonce}__(.*?)__END__\n"
SAFE_PATH_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_./\- ]{0,198}$")
ALLOWED_SUFFIXES = {".py", ".json", ".txt", ".csv", ".md"}


class ValidationError(ValueError):
    pass


def validate_files(files: Any) -> dict[str, str]:
    if not isinstance(files, dict) or not files:
        raise ValidationError("At least one file is required")
    if len(files) > MAX_FILES:
        raise ValidationError(f"Too many files (maximum {MAX_FILES})")
    cleaned: dict[str, str] = {}
    total = 0
    for raw_path, content in files.items():
        if not isinstance(raw_path, str) or not isinstance(content, str):
            raise ValidationError("Files must map names to source strings")
        path = raw_path.replace("\\", "/")
        while path.startswith("./"):
            path = path[2:]
        if (
            not path
            or path.startswith("/")
            or ".." in path.split("/")
            or not SAFE_PATH_RE.match(path)
            or Path(path).suffix.lower() not in ALLOWED_SUFFIXES
        ):
            raise ValidationError(f"Invalid file path: {raw_path[:80]}")
        data = content.encode("utf-8")
        if len(data) > MAX_FILE_BYTES:
            raise ValidationError(f"File too large: {path}")
        total += len(data)
        cleaned[path] = content
    if total > MAX_TOTAL_BYTES:
        raise ValidationError("Total source size exceeds the limit")
    return cleaned


def validate_tests(tests: Any) -> list[dict[str, Any]]:
    if not isinstance(tests, list) or len(tests) > MAX_TESTS:
        raise ValidationError(f"Provide at most {MAX_TESTS} tests")
    result = []
    for test in tests:
        if not isinstance(test, dict):
            raise ValidationError("Each test must be an object")
        if "assertion" in test:
            assertion = test["assertion"]
            if not isinstance(assertion, str) or len(assertion) > 4_000:
                raise ValidationError("Invalid assertion")
            result.append({"name": str(test.get("name", "Test"))[:100], "assertion": assertion,
                           "hidden": bool(test.get("hidden", False)), "kind": "assert"})
        elif "stdin" in test and "expect" in test:
            stdin = str(test["stdin"])
            expect = str(test["expect"])
            if len(stdin) > MAX_STDIN_BYTES or len(expect) > MAX_STDIN_BYTES:
                raise ValidationError("Input/output test is too large")
            result.append({"name": str(test.get("name", "Test"))[:100], "stdin": stdin,
                           "expect": expect, "hidden": bool(test.get("hidden", False)), "kind": "io"})
        else:
            raise ValidationError("Each test needs an assertion or stdin/expect")
    return result


def _run_process(
    workdir: Path,
    mode: str,
    entry: str,
    cpu: int,
    memory: int,
    stdin: str = "",
    assertion: str = "",
) -> dict[str, Any]:
    import base64

    nonce = secrets.token_hex(16)
    payload_re = re.compile(PAYLOAD_RE_TEMPLATE.format(nonce=nonce), re.DOTALL)

    cmd = [
        sys.executable, "-I", "-B", str(RUNNER),
        "--mode", mode,
        "--entry", entry,
        "--workdir", str(workdir),
        "--cpu", str(cpu),
        "--memory", str(memory),
        "--result-nonce", nonce,
    ]
    if assertion:
        cmd += ["--assertion-b64", base64.b64encode(assertion.encode("utf-8")).decode("ascii")]

    input_file = None
    if stdin:
        input_file = workdir / "__stdin__.txt"
        input_file.write_text(stdin, encoding="utf-8")
        cmd += ["--input-file", str(input_file)]

    # The child receives no inherited environment: no DATABASE_URL, SECRET_KEY
    # or any other credential from the web application.
    child_env = {"PATH": "/usr/local/bin:/usr/bin:/bin", "PYTHONIOENCODING": "utf-8"}
    started = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(workdir),
            env=child_env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=cpu + 2,
            stdin=subprocess.DEVNULL,
        )
        duration_ms = int((time.monotonic() - started) * 1000)
        raw_out = proc.stdout or ""
        match = payload_re.search(raw_out)
        visible_out = payload_re.sub("", raw_out).strip("\n")
        if match:
            import json

            try:
                payload = json.loads(match.group(1))
            except json.JSONDecodeError:
                payload = {"exit_code": 1, "stdout": visible_out, "stderr": proc.stderr or "",
                           "error": "Executor returned an invalid result", "truncated": False}
            # The trusted runner reports captured stdout inside the signed-by-nonce
            # payload. Anything printed directly to fd 1 is appended to it.
            payload["stdout"] = str(payload.get("stdout", "")) + visible_out
            payload["duration_ms"] = duration_ms
            return payload
        return {
            "exit_code": 1,
            "stdout": visible_out,
            "stderr": (proc.stderr or "")[:8_000],
            "error": "The execution did not complete normally",
            "truncated": False,
            "duration_ms": duration_ms,
        }
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout or b""
        if isinstance(out, bytes):
            out = out.decode("utf-8", errors="replace")
        return {
            "exit_code": 124,
            "stdout": str(out).strip("\n"),
            "stderr": "",
            "error": f"Execution timed out after {cpu} seconds",
            "truncated": True,
            "duration_ms": int((time.monotonic() - started) * 1000),
            "timed_out": True,
        }
    finally:
        if input_file and input_file.exists():
            input_file.unlink(missing_ok=True)


def execute(payload: dict[str, Any], work_root: str, default_cpu: int, default_memory: int) -> dict[str, Any]:
    """Execute code or grade a submission. Always cleans up its workspace."""
    files = validate_files(payload.get("files"))
    entry = str(payload.get("entrypoint", "main.py")).replace("\\", "/").lstrip("./")
    if entry not in files or not entry.endswith(".py"):
        raise ValidationError("Entrypoint must be one of the submitted .py files")
    stdin = str(payload.get("stdin", ""))
    if len(stdin) > MAX_STDIN_BYTES:
        raise ValidationError("Input is too large")
    cpu = min(max(int(payload.get("timeout_seconds", default_cpu) or default_cpu), 1), 15)
    memory = min(max(int(payload.get("memory_mb", default_memory) or default_memory), 64), 512)
    mode = payload.get("mode", "run")
    if mode not in {"run", "test"}:
        raise ValidationError("Unknown execution mode")

    root = Path(work_root)
    root.mkdir(parents=True, exist_ok=True)
    workdir = Path(tempfile.mkdtemp(prefix="run-", dir=str(root)))
    try:
        for path, content in files.items():
            target = workdir / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        os.chmod(workdir, 0o700)

        if mode == "run":
            result = _run_process(workdir, "run", entry, cpu, memory, stdin=stdin)
            return {
                "status": "ok" if result.get("exit_code") == 0 else "error",
                "stdout": result.get("stdout", ""),
                "stderr": result.get("stderr", ""),
                "error": result.get("error"),
                "duration_ms": result.get("duration_ms", 0),
                "truncated": bool(result.get("truncated")),
                "timed_out": bool(result.get("timed_out")),
            }

        tests = validate_tests(payload.get("tests"))
        if not tests:
            raise ValidationError("At least one test is required")
        solution_path = workdir / "solution.py"
        if entry != "solution.py":
            solution_path.write_text(files[entry], encoding="utf-8")

        results = []
        total_ms = 0
        for test in tests:
            if test["kind"] == "assert":
                run = _run_process(workdir, "assert", "solution.py", cpu, memory, assertion=test["assertion"])
                detail = run.get("error") or run.get("stderr", "")
                passed = run.get("exit_code") == 0
                expected_display = "" if test["hidden"] else "all assertions passed"
                actual_display = "" if passed or test["hidden"] else (detail[:1_000] or "assertion failed")
            else:
                run = _run_process(workdir, "run", entry, cpu, memory, stdin=test["stdin"])
                actual = str(run.get("stdout", "")).strip().replace("\r\n", "\n")
                expected = test["expect"].strip().replace("\r\n", "\n")
                passed = actual == expected and run.get("exit_code") == 0
                expected_display = "" if test["hidden"] else expected
                actual_display = "" if test["hidden"] else actual
                detail = run.get("error") or run.get("stderr", "")
                if not passed and not detail:
                    detail = "Output did not match the expected result"
            total_ms += int(run.get("duration_ms", 0))
            results.append({
                "name": test["name"],
                "hidden": test["hidden"],
                "passed": passed,
                "expected": expected_display,
                "actual": actual_display,
                "error": detail[:1_500],
                "timed_out": bool(run.get("timed_out")),
            })
        passed_count = sum(1 for r in results if r["passed"])
        return {
            "status": "passed" if passed_count == len(results) else "failed",
            "passed": passed_count,
            "total": len(results),
            "results": results,
            "duration_ms": total_ms,
        }
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
