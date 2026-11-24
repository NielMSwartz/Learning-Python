"""Small builders that keep curriculum data readable and testable."""

from __future__ import annotations

import builtins
from typing import Any


def A(name: str, assertion: str, hidden: bool = False) -> dict:
    """A behavioural test: the assertion runs against the learner's module."""
    return {"name": name, "assertion": assertion, "hidden": hidden}


def I(name: str, stdin: str, expect: str) -> dict[str, str]:
    """An input/output test: stdin is fed to the learner's script."""
    return {"name": name, "stdin": stdin, "expect": expect}


def _source(value: Any) -> str:
    """Render a curriculum value as executable Python source.

    ``repr`` is not sufficient for callables: ``repr(round)`` produces
    ``<built-in function round>``, which cannot be compiled. Only named
    builtins are supported; use ``A(...)`` with a raw assertion for custom
    callables such as lambdas.
    """
    if callable(value):
        name = getattr(value, "__name__", None)
        if name and hasattr(builtins, name) and getattr(builtins, name) is value:
            return name
        raise ValueError("Callable test arguments must be named builtins; use A() for custom callables")
    if isinstance(value, tuple):
        items = ", ".join(_source(item) for item in value)
        return f"({items},)" if len(value) == 1 else f"({items})"
    if isinstance(value, list):
        return "[" + ", ".join(_source(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{" + ", ".join(f"{_source(key)}: {_source(item)}" for key, item in value.items()) + "}"
    if isinstance(value, set):
        return "{" + ", ".join(_source(item) for item in sorted(value, key=repr)) + "}" if value else "set()"
    return repr(value)


def source(value: Any) -> str:
    """Public alias used by curriculum builders that render examples."""
    return _source(value)


def arguments_source(args: Any) -> str:
    """Render a call's arguments; a tuple is unpacked, other values are single."""
    if isinstance(args, tuple):
        return ", ".join(_source(arg) for arg in args)
    return _source(args)


def assertion_for(fn: str, args: Any, expected: Any) -> str:
    """Build a behavioural assertion against the learner's ``solution`` module."""
    return f"assert solution.{fn}({arguments_source(args)}) == {_source(expected)}"


def calls(fn: str, cases: list[tuple[Any, Any]], label: str = "Case") -> list[dict[str, str]]:
    """Build assertion tests from (arguments, expected result) pairs.

    A tuple of arguments is unpacked into the call; any other value is passed
    as one argument. For example, ``((2, 3), 5)`` becomes ``fn(2, 3) == 5``
    while ``([1, 2], 3)`` becomes ``fn([1, 2]) == 3``.
    """
    return [
        A(f"{label} {index}", assertion_for(fn, args, expected))
        for index, (args, expected) in enumerate(cases, start=1)
    ]


def T(
    slug: str,
    title: str,
    level: int,
    category: str,
    summary: str,
    explanation: str,
    examples: list[dict[str, str]],
    mistakes: list[str],
    why: str,
    exercise: dict,
) -> dict:
    return dict(
        slug=slug,
        title=title,
        level=level,
        category=category,
        summary=summary,
        explanation=explanation,
        examples=examples,
        mistakes=mistakes,
        why_useful=why,
        exercise=exercise,
    )


def ex(slug: str, prompt: str, starter: str, tests: list[dict[str, str]]) -> dict:
    return {"slug": slug, "prompt": prompt, "starter_code": starter, "tests": tests}


def P(
    slug: str,
    title: str,
    level: int,
    subtitle: str,
    intro: str,
    outcomes: list[str],
    concepts: list[str],
    objectives: list[str],
    steps: list[tuple[str, str, str]],
    requirements: list[str],
    tests: list[dict[str, str]],
    starter: str,
    summary: str,
    minutes: int = 90,
) -> dict:
    return dict(
        slug=slug,
        title=title,
        level=level,
        subtitle=subtitle,
        intro=intro,
        outcomes=outcomes,
        concepts=concepts,
        objectives=objectives,
        steps=[
        {"title": step[0], "detail": step[1], "hint": step[2] if len(step) > 2 else ""}
        for step in steps
    ],
        requirements=requirements,
        tests=tests,
        starter_code=starter,
        summary=summary,
        estimated_minutes=minutes,
    )
