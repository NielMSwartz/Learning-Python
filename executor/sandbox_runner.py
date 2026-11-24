"""Trusted launcher for learner code.

This script is part of the isolated executor image (never the Flask web app).
It applies process-level restrictions *before* importing or running any user
file, patches network primitives, and caps output. In production the container
adds filesystem, CPU, memory, PID and capability restrictions on top of this.
"""

from __future__ import annotations

import argparse
import base64
import builtins
import importlib.util
import os
import runpy
import socket
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


class OutputLimitExceeded(Exception):
    pass


class CappedWriter:
    """A text stream that stops runaway output from filling executor memory."""

    def __init__(self, limit: int = 65_536):
        self.limit = limit
        self.parts: list[str] = []
        self.size = 0
        self.truncated = False

    def write(self, text: str) -> int:
        if not isinstance(text, str):
            text = str(text)
        remaining = self.limit - self.size
        if remaining <= 0:
            self.truncated = True
            return len(text)
        if len(text) > remaining:
            self.truncated = True
            text = text[:remaining]
        self.parts.append(text)
        self.size += len(text)
        return len(text)

    def flush(self) -> None:
        return None

    def getvalue(self) -> str:
        return "".join(self.parts)


def block_network() -> None:
    """Remove the common socket entry points from user code."""
    def denied(*args, **kwargs):
        raise PermissionError("Network access is disabled in the code sandbox")

    for name in ("create_connection", "getaddrinfo", "gethostbyname", "socketpair"):
        if hasattr(socket, name):
            setattr(socket, name, denied)
    original_socket = socket.socket

    class BlockedSocket(original_socket):  # type: ignore[misc, valid-type]
        def connect(self, *args, **kwargs):
            raise PermissionError("Network access is disabled in the code sandbox")

        def connect_ex(self, *args, **kwargs):
            raise PermissionError("Network access is disabled in the code sandbox")

        def sendto(self, *args, **kwargs):
            raise PermissionError("Network access is disabled in the code sandbox")

    socket.socket = BlockedSocket  # type: ignore[assignment]
    for module_name in ("http.client", "urllib.request", "asyncio"):
        sys.modules.pop(module_name, None)


def apply_limits(cpu_seconds: int, memory_mb: int) -> None:
    """Best-effort OS limits. Docker limits are the real boundary in production."""
    try:
        import resource  # POSIX only
    except ImportError:
        return

    def set_limit(name: str, value: int) -> None:
        try:
            soft = getattr(resource, name)
            resource.setrlimit(soft, (value, value))
        except (ValueError, OSError):
            pass

    set_limit("RLIMIT_CPU", max(1, cpu_seconds))
    memory_bytes = max(64, memory_mb) * 1024 * 1024
    set_limit("RLIMIT_AS", memory_bytes)
    set_limit("RLIMIT_FSIZE", 2 * 1024 * 1024)
    set_limit("RLIMIT_NOFILE", 64)
    if hasattr(resource, "RLIMIT_CORE"):
        set_limit("RLIMIT_CORE", 0)


def load_solution(path: Path):
    """Import the learner's entry module under the name ``solution``."""
    spec = importlib.util.spec_from_file_location("solution", path)
    if spec is None or spec.loader is None:
        raise ImportError("Could not load the submitted file")
    module = importlib.util.module_from_spec(spec)
    sys.modules["solution"] = module
    spec.loader.exec_module(module)
    return module


def format_user_traceback(exc: BaseException, workdir: Path) -> str:
    """Build a familiar traceback containing only the learner's own frames."""
    import traceback

    lines = ["Traceback (most recent call last):"]
    for frame in traceback.extract_tb(exc.__traceback__):
        path = Path(frame.filename)
        try:
            path.relative_to(workdir)
        except ValueError:
            continue  # hide trusted runner internals
        lines.append(f'  File "{path.name}", line {frame.lineno}, in {frame.name}')
        if frame.line:
            lines.append(f"    {frame.line.strip()}")
    lines.extend(traceback.format_exception_only(type(exc), exc))
    return "\n".join(lines).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["run", "assert"], required=True)
    parser.add_argument("--entry", required=True)
    parser.add_argument("--workdir", required=True)
    parser.add_argument("--cpu", type=int, default=5)
    parser.add_argument("--memory", type=int, default=192)
    parser.add_argument("--assertion-b64", default="")
    parser.add_argument("--input-file", default="")
    parser.add_argument("--result-nonce", default="")
    args = parser.parse_args()

    workdir = Path(args.workdir).resolve()
    os.chdir(workdir)
    sys.path.insert(0, str(workdir))

    # Only the executor's own minimal variables survive, and even those are
    # hidden from submitted code.
    os.environ.clear()

    apply_limits(args.cpu, args.memory)
    block_network()

    stdout = CappedWriter()
    stderr = CappedWriter()
    exit_code = 0
    error: str | None = None

    # Input is supplied through a file so arbitrary binary/newline content is safe.
    if args.input_file:
        try:
            sys.stdin = open(args.input_file, "r", encoding="utf-8", errors="replace")
        except OSError:
            sys.stdin = open(os.devnull, "r", encoding="utf-8")

    # Restrict dangerous introspection helpers often used to escape sandboxes.
    for name in ("exit", "quit"):
        if hasattr(builtins, name):
            delattr(builtins, name)

    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            if args.mode == "run":
                runpy.run_path(str(Path(args.entry).resolve()), run_name="__main__")
            else:
                solution = load_solution(Path(args.entry).resolve())
                assertion = base64.b64decode(args.assertion_b64).decode("utf-8")
                exec(compile(assertion, "<hidden test>", "exec"), {"solution": solution, "__builtins__": builtins})
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 0
    except OutputLimitExceeded:
        error = "Output limit exceeded"
    except BaseException as exc:  # tracebacks are returned to the learner
        error = format_user_traceback(exc, workdir)
        exit_code = 1
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    import json

    payload = {
        "exit_code": exit_code,
        "stdout": stdout.getvalue(),
        "stderr": stderr.getvalue(),
        "truncated": stdout.truncated or stderr.truncated,
        "error": error,
    }
    # A per-run nonce prevents submitted code from forging the result marker.
    marker = f"\n__PAYLOAD_{args.result_nonce}__" + json.dumps(payload) + "__END__\n"
    # Write directly to fd 1: user code may have replaced or closed sys.stdout.
    try:
        os.write(1, marker.encode("utf-8"))
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
