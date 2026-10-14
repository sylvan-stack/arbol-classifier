"""`classify` as one piece: what it adds, that it starts nothing but what prints the key (ARC-0.30), the attempts
and the waits (CLS-0.11), and the table of errors (CLS-0.12)."""

import json
import subprocess
import sys
import time
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from stand_ins import security_stand_in

from arbol_classifier.classify import classify
from arbol_classifier.errors import Failure
from arbol_classifier.key import ACCOUNT, SERVICE
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
    def test_adds_the_key_the_pinned_model_and_the_limits(self) -> None:
        settings = Settings(model="jev-1.14.0", max_request_bytes=500, endpoint="http://127.0.0.1:8649/v1/systemone")
        send = FakeJev()
        result = classify(json.dumps(REQUEST).encode(), settings, FILE, Deadline(4.5), send=send, key=fixed_key)
        [(endpoint, body, key, timeout)] = send.calls
        self.assertEqual((endpoint, key, timeout), ("http://127.0.0.1:8649/v1/systemone", "key-marker", 4.5))
        self.assertEqual(json.loads(body), {**REQUEST, "model": "jev-1.14.0"})
        self.assertEqual(result, {"model": "jev-1.14.0", "answers": {"work": {"type": "noul", "noul": 0.9}}})
        with self.assertRaises(Failure) as caught:
            classify(json.dumps(REQUEST).encode(), Settings(max_request_bytes=len(body) - 1), FILE, Deadline(4.5),
                     send=send, key=fixed_key)
        self.assertEqual((caught.exception.code, len(send.calls)), ("invalid_input", 1))

    def test_interprets_no_question(self) -> None:
        request = {"state": [1, {"a": None}], "questions": {"work": {"type": "rank", "instructions": None, "x": 1}}}
        send = FakeJev()
        classify(json.dumps(request).encode(), Settings(), FILE, Deadline(10), send=send, key=fixed_key)
        self.assertEqual(json.loads(send.calls[0][1]), {**request, "model": "jev-1.13.0"})

    def test_a_refused_request_reads_no_key_and_sends_nothing(self) -> None:
        send = FakeJev()
        keys: list[Settings] = []

        def key(settings: Settings, settings_file: Path, deadline: Deadline) -> str:
            keys.append(settings)
            return "key-marker"

        for data in (b"{", json.dumps({**REQUEST, "model": "jev-1.13.0"}).encode(),
                     json.dumps({**REQUEST, "state": "x" * 64000}).encode()):
            with self.assertRaises(Failure):
                classify(data, Settings(), FILE, Deadline(10), send=send, key=key)
        self.assertEqual((keys, send.calls), ([], []))

    def test_starts_nothing_but_the_key_command(self) -> None:
        started: list[list[str]] = []
        original = subprocess.Popen.__init__

        def recording(popen: subprocess.Popen[bytes], args: Any, *rest: Any, **options: Any) -> None:
            started.append(list(args))
            original(popen, args, *rest, **options)

        command = (sys.executable, "-I", "-B", "-c", "print('key-marker')")
        send = FakeJev()
        with patch.object(subprocess.Popen, "__init__", recording):
            classify(json.dumps(REQUEST).encode(), Settings(secret_command=command), FILE, Deadline(10), send=send)
        self.assertEqual(started, [list(command)])
        self.assertEqual(send.calls[0][2], "key-marker")

    def test_starts_nothing_but_security_for_the_key_from_the_keychain(self) -> None:
        security = security_stand_in(self)
        security.put(SERVICE, ACCOUNT, "key-marker-item")
        started: list[list[str]] = []
        original = subprocess.Popen.__init__

        def recording(popen: subprocess.Popen[bytes], args: Any, *rest: Any, **options: Any) -> None:
            started.append(list(args))
            original(popen, args, *rest, **options)

        send = FakeJev()
        with patch.object(subprocess.Popen, "__init__", recording):
            classify(json.dumps(REQUEST).encode(), Settings(), FILE, Deadline(10), send=send)
        self.assertEqual(started, [[str(security.program), "find-generic-password", "-s", SERVICE, "-a", ACCOUNT, "-w"]])
        self.assertEqual(send.calls[0][2], "key-marker-item")


class Errors(unittest.TestCase):
    """Each status of Jev, and a failed connection, gets its code of CLS-0, "Errors"."""

    def setUp(self) -> None:
        replacement = patch("arbol_classifier.limits.SCALE", 0.001)
        replacement.start()
        self.addCleanup(replacement.stop)

    def test_statuses_that_no_further_attempt_can_help(self) -> None:
        for status, code in ((401, "credential_rejected"), (422, "invalid_input"), (413, "invalid_input"),
                             (400, "vendor_error"), (403, "vendor_error"), (404, "vendor_error"), (302, "vendor_error"),
                             (418, "vendor_error")):
            with self.subTest(status=status):
                send = FakeJev(status, 200)
                failure = failure_of(self, send)
                self.assertEqual((failure.code, len(send.calls)), (code, 1))
                self.assertEqual(failure.error()["detail"], {"basis": "fields", "vendorStatus": status})
                self.assertFalse(failure.error()["retryable"])

    def test_statuses_and_failed_connections_that_are_tried_again(self) -> None:
        unreachable = Failure("vendor_unavailable", "Jev could not be reached at http://127.0.0.1:9/v1/systemone.")
        for status, code in ((429, "rate_limited"), (529, "vendor_unavailable"), (500, "vendor_unavailable"),
                             (502, "vendor_unavailable"), (503, "vendor_unavailable"), (599, "vendor_unavailable"),
                             (unreachable, "vendor_unavailable")):
            with self.subTest(status=status):
                send = FakeJev(status)
                failure = failure_of(self, send)
                self.assertEqual((failure.code, len(send.calls)), (code, 3))
                self.assertTrue(failure.error()["retryable"])
                self.assertIn("Attempts made: 3", str(failure))

    def test_a_further_attempt_that_succeeds(self) -> None:
        unreachable = Failure("vendor_unavailable", "Jev could not be reached.")
        for statuses in ((529, 200), (429, 500, 200), (unreachable, 200), (unreachable, 429, 200)):
            with self.subTest(statuses=statuses):
                send = FakeJev(*statuses)
                self.assertEqual(call(send), {"model": "jev-1.13.0", "answers": {"work": {"type": "noul", "noul": 0.9}}})
                self.assertEqual(len(send.calls), len(statuses))

    def test_a_further_attempt_only_where_it_can_help(self) -> None:
        for statuses, code, attempts in (((529, 401), "credential_rejected", 2), ((429, 422), "invalid_input", 2),
                                         ((500, 400), "vendor_error", 2)):
            with self.subTest(statuses=statuses):
                send = FakeJev(*statuses)
                failure = failure_of(self, send)
                self.assertEqual((failure.code, len(send.calls)), (code, attempts))
        stopped = FakeJev(200, reply={"model": "jev-9.9.9", "answers": {}})
        self.assertEqual((failure_of(self, stopped).code, len(stopped.calls)), ("vendor_error", 1))

    def test_rate_limited_names_the_time_jev_named(self) -> None:
        failure = failure_of(self, FakeJev(429, retry_after=7))
        self.assertEqual(failure.error()["retryAfterSeconds"], 7)
        self.assertNotIn("retryAfterSeconds", failure_of(self, FakeJev(429)).error())
        self.assertNotIn("retryAfterSeconds", failure_of(self, FakeJev(503, retry_after=7)).error())

    def test_the_message_says_what_jev_said_without_the_judged_text_or_the_key(self) -> None:
        cases: tuple[tuple[object, str], ...] = (
            ({"detail": [{"loc": ["body", "questions", "work", "criteria"], "msg": "Field required", "type": "missing",
                          "input": "judged marker"}]}, "body.questions.work.criteria: Field required"),
            ({"detail": "Too many tokens in judged marker"}, "Too many tokens in …"),
            ({"message": "Invalid API key key-marker"}, "Invalid API key …"),
            ({"error": {"message": "Model jev-1.13.0 is retired", "input": "judged marker"}},
             "Model jev-1.13.0 is retired"),
            ({"error": "x" * 400}, "x" * 299 + "…"),
        )
        for reply, said in cases:
            with self.subTest(reply=reply):
                failure = failure_of(self, FakeJev(422, reply=reply))
                self.assertEqual(str(failure), f"Jev refused the request as invalid: {said}")
                self.assertIn(said, str(failure_of(self, FakeJev(401, reply=reply))))
        failure = failure_of(self, FakeJev(422, reply=["judged marker"]))
        self.assertEqual(
            str(failure), "Jev refused the request as invalid (HTTP status 422) and gave no reason that can be shown."
        )


class Attempts(unittest.TestCase):
    """At most three attempts, after waits of half a second and one second, never past the time limit (CLS-0.9, 0.11)."""

    def test_the_waits_between_attempts(self) -> None:
        with patch("arbol_classifier.limits.SCALE", 0.1):
            send = FakeJev(529)
            failure_of(self, send)
        first, second, third = send.times
        self.assertGreaterEqual(second - first, 0.05)
        self.assertLess(second - first, 0.09)
        self.assertGreaterEqual(third - second, 0.1)
        self.assertLess(third - second, 0.14)

    def test_no_wait_goes_past_the_time_limit(self) -> None:
        # Scaled by 0.1: a limit of 0.12 s holds the first wait of 0.05 s, not the second of 0.1 s.
        with patch("arbol_classifier.limits.SCALE", 0.1):
            started = time.monotonic()
            send = FakeJev(529)
            failure = failure_of(self, send, seconds=1.2)
        self.assertEqual((failure.code, len(send.calls)), ("vendor_unavailable", 2))
        self.assertLess(time.monotonic() - started, 0.12)
        self.assertIn("Attempts made: 2", str(failure))

    def test_a_slow_key_reaches_the_time_limit(self) -> None:
        command = (sys.executable, "-I", "-B", "-c", "import time; time.sleep(5)")
        send = FakeJev()
        started = time.monotonic()
        with patch("arbol_classifier.limits.SCALE", 0.1), self.assertRaises(Failure) as caught:
            classify(json.dumps(REQUEST).encode(), Settings(secret_command=command), FILE, Deadline(3), send=send)
        self.assertLess(time.monotonic() - started, 2)
        self.assertEqual((caught.exception.code, send.calls), ("limit_reached", []))
        self.assertIn("3 seconds", str(caught.exception))
