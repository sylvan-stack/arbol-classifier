# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
"""One attempt at Jev, with a fake connection: only the endpoint's address, the key as a bearer token, and an
attempt that cannot outlast the time limit of the call (CLS-0.5, 0.9, 0.13)."""

from arbol_classifier import jev
from arbol_classifier.errors import Failure
from arbol_classifier.limits import Deadline


import http.client
import time
import unittest
from typing import Any
from unittest.mock import patch


class FakeSocket:
    def __init__(self, peer: str) -> None:
        self.peer = peer

    def getpeername(self) -> tuple[str, int]:
        return self.peer, 443


class FakeResponse:
    status = 200
    retry_after: str | None = None
    slow = 0.0

    def getheader(self, name: str) -> str | None:
        return FakeResponse.retry_after if name == "Retry-After" else None

    def read(self) -> bytes:
        time.sleep(FakeResponse.slow)
        return b'{"answer": true}'


class FakeConnection:
    made: list[FakeConnection] = []
    peer = "127.0.0.1"
    fail: BaseException | None = None

    def __init__(self, host: str, port: int | None, timeout: float, context: Any = None) -> None:
        self.host, self.port, self.timeout, self.context = host, port, timeout, context
        self.sock: FakeSocket | None = None
        self.requests: list[tuple[str, str, bytes, dict[str, str]]] = []
        self.closed = False
        FakeConnection.made.append(self)

    def connect(self) -> None:
        self.sock = FakeSocket(FakeConnection.peer)

    def request(self, method: str, path: str, body: bytes, headers: dict[str, str]) -> None:
        if FakeConnection.fail is not None:
            raise FakeConnection.fail
        self.requests.append((method, path, body, headers))

    def getresponse(self) -> FakeResponse:
        return FakeResponse()

    def close(self) -> None:
        self.closed = True


class Transport(unittest.TestCase):
    def setUp(self) -> None:
        FakeConnection.made = []
        FakeConnection.peer = "127.0.0.1"
        FakeConnection.fail = None
        FakeResponse.retry_after = None
        FakeResponse.slow = 0.0
        for name in ("HTTPConnection", "HTTPSConnection"):
            patcher = patch.object(http.client, name, FakeConnection)
            patcher.start()
            self.addCleanup(patcher.stop)


# Archived complete imports; restore needed names in their original scope, not at this file tail.
