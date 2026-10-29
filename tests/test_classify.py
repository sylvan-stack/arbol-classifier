# Shared fixtures only; test bodies are in top/ and mid/. See TESTS.md.
"""`classify` as one piece: what it adds, that it starts nothing but what prints the key (ARC-0.30), the attempts
and the waits (CLS-0.11), and the table of errors (CLS-0.12)."""

import json
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from arbol_classifier.classify import classify
from arbol_classifier.errors import Failure
from arbol_classifier.limits import Deadline
from arbol_classifier.settings import Settings

FILE = Path("/Users/someone/.arbol/arbol-classifier.json")
REQUEST = {"state": "judged marker", "questions": {"work": {"type": "noul", "instructions": "Work?"}}}


class FakeJev:
    """Answers each attempt with the next of `statuses`; the last one repeats. A Failure stands for a failed connection."""

    def __init__(self, *statuses: int | Failure, reply: object | None = None, retry_after: int | None = None) -> None:
        self.statuses = list(statuses) or [200]
        self.reply = reply
        self.retry_after = retry_after
        self.calls: list[tuple[str, bytes, str, float]] = []
        self.times: list[float] = []

    def __call__(self, endpoint: str, body: bytes, key: str, deadline: Deadline) -> tuple[int, bytes, int | None]:
        self.calls.append((endpoint, body, key, deadline.seconds))
        self.times.append(time.monotonic())
        status = self.statuses[min(len(self.calls), len(self.statuses)) - 1]
        if isinstance(status, Failure):
            raise status
        model = json.loads(body)["model"]
        reply = self.reply or {"model": model, "answers": {"work": {"type": "noul", "noul": 0.9}}}
        return status, json.dumps(reply).encode("utf-8"), self.retry_after


def fixed_key(settings: Settings, settings_file: Path, deadline: Deadline) -> str:
    return "key-marker"


def call(send: FakeJev, settings: Settings | None = None, seconds: float = 10) -> object:
    return classify(json.dumps(REQUEST).encode(), settings or Settings(), FILE, Deadline(seconds), send=send,
                    key=fixed_key)


def failure_of(test: unittest.TestCase, send: FakeJev, seconds: float = 10) -> Failure:
    with test.assertRaises(Failure) as caught:
        call(send, seconds=seconds)
    test.assertNotIn("judged marker", str(caught.exception))
    test.assertNotIn("key-marker", str(caught.exception))
    return caught.exception


class Classify(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


class Errors(unittest.TestCase):
    """Each status of Jev, and a failed connection, gets its code of CLS-0, "Errors"."""

    def setUp(self) -> None:
        replacement = patch("arbol_classifier.limits.SCALE", 0.001)
        replacement.start()
        self.addCleanup(replacement.stop)


class Attempts(unittest.TestCase):
    """At most three attempts, after waits of half a second and one second, never past the time limit (CLS-0.9, 0.11)."""


# Archived complete imports; restore needed names in their original scope, not at this file tail.
