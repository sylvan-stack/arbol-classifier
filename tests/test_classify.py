"""`classify` as one piece: what it adds, and that it starts nothing but what prints the key (ARC-0.30)."""

import json
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from stand_ins import security_stand_in

from arbol_classifier.classify import classify
from arbol_classifier.errors import Failure
from arbol_classifier.key import ACCOUNT, SERVICE
from arbol_classifier.settings import Settings

FILE = Path("/Users/someone/.arbol/arbol-classifier.json")
REQUEST = {"state": "judged marker", "questions": {"work": {"type": "noul", "instructions": "Work?"}}}


class FakeJev:
    def __init__(self, status: int = 200, reply: object | None = None) -> None:
        self.status = status
        self.reply = reply
        self.calls: list[tuple[str, bytes, str, float]] = []

    def __call__(self, endpoint: str, body: bytes, key: str, timeout: float) -> tuple[int, bytes]:
        self.calls.append((endpoint, body, key, timeout))
        model = json.loads(body)["model"]
        reply = self.reply or {"model": model, "answers": {"work": {"type": "noul", "noul": 0.9}}}
        return self.status, json.dumps(reply).encode("utf-8")


def fixed_key(settings: Settings, settings_file: Path, timeout: float) -> str:
    return "key-marker"


class Classify(unittest.TestCase):
    def test_adds_the_key_the_pinned_model_and_the_limits(self) -> None:
        settings = Settings(model="jev-1.14.0", max_request_bytes=500, endpoint="http://127.0.0.1:8649/v1/systemone")
        send = FakeJev()
        result = classify(json.dumps(REQUEST).encode(), settings, FILE, 4.5, send=send, key=fixed_key)
        [(endpoint, body, key, timeout)] = send.calls
        self.assertEqual((endpoint, key, timeout), ("http://127.0.0.1:8649/v1/systemone", "key-marker", 4.5))
        self.assertEqual(json.loads(body), {**REQUEST, "model": "jev-1.14.0"})
        self.assertEqual(result, {"model": "jev-1.14.0", "answers": {"work": {"type": "noul", "noul": 0.9}}})
        with self.assertRaises(Failure) as caught:
            classify(json.dumps(REQUEST).encode(), Settings(max_request_bytes=len(body) - 1), FILE, 4.5, send=send,
                     key=fixed_key)
        self.assertEqual((caught.exception.code, len(send.calls)), ("invalid_input", 1))

    def test_interprets_no_question(self) -> None:
        request = {"state": [1, {"a": None}], "questions": {"work": {"type": "rank", "instructions": None, "x": 1}}}
        send = FakeJev()
        classify(json.dumps(request).encode(), Settings(), FILE, 10, send=send, key=fixed_key)
        self.assertEqual(json.loads(send.calls[0][1]), {**request, "model": "jev-1.13.0"})

    def test_a_refused_request_reads_no_key_and_sends_nothing(self) -> None:
        send = FakeJev()
        keys: list[Settings] = []

        def key(settings: Settings, settings_file: Path, timeout: float) -> str:
            keys.append(settings)
            return "key-marker"

        for data in (b"{", json.dumps({**REQUEST, "model": "jev-1.13.0"}).encode(),
                     json.dumps({**REQUEST, "state": "x" * 64000}).encode()):
            with self.assertRaises(Failure):
                classify(data, Settings(), FILE, 10, send=send, key=key)
        self.assertEqual((keys, send.calls), ([], []))

    def test_a_status_other_than_200_fails(self) -> None:
        # The table of errors comes with SYL-162; until then any other status is a vendor_error.
        for status in (401, 422, 429, 500, 529, 302):
            with self.subTest(status=status), self.assertRaises(Failure) as caught:
                classify(json.dumps(REQUEST).encode(), Settings(), FILE, 10, send=FakeJev(status), key=fixed_key)
            self.assertEqual(caught.exception.code, "vendor_error")
            self.assertNotIn("judged marker", str(caught.exception))

    def test_starts_nothing_but_the_key_command(self) -> None:
        started: list[list[str]] = []
        original = subprocess.Popen.__init__

        def recording(popen: subprocess.Popen[bytes], args: Any, *rest: Any, **options: Any) -> None:
            started.append(list(args))
            original(popen, args, *rest, **options)

        command = (sys.executable, "-I", "-B", "-c", "print('key-marker')")
        send = FakeJev()
        with patch.object(subprocess.Popen, "__init__", recording):
            classify(json.dumps(REQUEST).encode(), Settings(secret_command=command), FILE, 10, send=send)
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
            classify(json.dumps(REQUEST).encode(), Settings(), FILE, 10, send=send)
        self.assertEqual(started, [[str(security.program), "find-generic-password", "-s", SERVICE, "-a", ACCOUNT, "-w"]])
        self.assertEqual(send.calls[0][2], "key-marker-item")
