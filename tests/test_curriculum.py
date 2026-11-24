"""Curriculum integrity: every authored test must be executable source."""

from __future__ import annotations

from app.curriculum.challenges import CHALLENGES
from app.curriculum.helpers import calls
from app.seed import ALL_PROJECTS, ALL_TOPICS


def _all_tests():
    for topic in ALL_TOPICS:
        yield from topic["exercise"]["tests"]
    for project in ALL_PROJECTS:
        yield from project["tests"]
    for challenge in CHALLENGES:
        yield from challenge["tests"]


def test_calls_helper_unpacks_arguments_and_renders_builtins():
    assert calls("add", [((2, 3), 5)])[0]["assertion"] == "assert solution.add(2, 3) == 5"
    assert calls("initials", [("Ada Lovelace", "A.L")])[0]["assertion"] == (
        "assert solution.initials('Ada Lovelace') == 'A.L'"
    )
    assert calls("total", [(([1.2, 2.3], round), 3)])[0]["assertion"] == (
        "assert solution.total([1.2, 2.3], round) == 3"
    )


def test_challenge_calls_unpack_their_arguments():
    challenge = next(item for item in CHALLENGES if item["slug"] == "sum-of-list")
    assert challenge["tests"][0]["assertion"] == "assert solution.sum_numbers([1, 2, 3]) == 6"
    assert challenge["examples"][0] == {"input": "sum_numbers([1, 2, 3])", "output": "6"}


def test_every_authored_assertion_compiles():
    assertions = [test["assertion"] for test in _all_tests() if "assertion" in test]
    assert len(assertions) > 100
    for source in assertions:
        compile(source, "<curriculum test>", "exec")


def test_input_tests_have_text_contracts():
    io_tests = [test for test in _all_tests() if "stdin" in test]
    for test in io_tests:
        assert isinstance(test["stdin"], str)
        assert isinstance(test["expect"], str)
        assert test["expect"]
