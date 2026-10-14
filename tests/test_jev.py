"""The call to Jev, with a fake connection: only the endpoint's address, the key as a bearer token (CLS-0.5, 0.13)."""

import http.client
import unittest
from typing import Any
from unittest.mock import patch

from arbol_classifier import jev
from arbol_classifier.errors import Failure


class FakeSocket:
    def __init__(self, peer: str) -> None:
        self.peer = peer

    def getpeername(self) -> tuple[str, int]:
        return self.peer, 443


class FakeResponse:
    status = 200

    def read(self) -> bytes:
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
        for name in ("HTTPConnection", "HTTPSConnection"):
            patcher = patch.object(http.client, name, FakeConnection)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_the_body_goes_to_the_endpoint_with_the_key_as_a_bearer_token(self) -> None:
        FakeConnection.peer = "203.0.113.7"
        status, answer = jev.post("https://api.typesafe.ai/v1/systemone", b'{"state":"x"}', "key-marker", 7.5)
        self.assertEqual((status, answer), (200, b'{"answer": true}'))
        [connection] = FakeConnection.made
        self.assertEqual((connection.host, connection.port, connection.timeout), ("api.typesafe.ai", None, 7.5))
        self.assertIsNotNone(connection.context)
        self.assertEqual(
            connection.requests,
            [("POST", "/v1/systemone", b'{"state":"x"}', {"Authorization": "Bearer key-marker",
                                                          "Content-Type": "application/json",
                                                          "User-Agent": "arbol-classifier"})],
        )
        self.assertTrue(connection.closed)

    def test_an_address_on_this_mac(self) -> None:
        for endpoint, peer, host, port, path in (
            ("http://127.0.0.1:8649/v1/systemone", "127.0.0.1", "127.0.0.1", 8649, "/v1/systemone"),
            ("http://localhost:9/x?y=1", "::1", "localhost", 9, "/x?y=1"),
            ("https://[::1]:7000/v1/systemone", "::1", "::1", 7000, "/v1/systemone"),
            ("http://localhost", "::ffff:127.0.0.1", "localhost", None, "/"),
        ):
            with self.subTest(endpoint=endpoint):
                FakeConnection.made = []
                FakeConnection.peer = peer
                jev.post(endpoint, b"{}", "key", 10)
                [connection] = FakeConnection.made
                self.assertEqual((connection.host, connection.port, connection.requests[0][1]), (host, port, path))

    def test_an_endpoint_on_this_mac_that_leads_elsewhere_is_refused_before_anything_is_sent(self) -> None:
        for peer in ("192.168.1.20", "203.0.113.7", "::ffff:192.168.1.20", "fe80::1%en0", ""):
            with self.subTest(peer=peer):
                FakeConnection.made = []
                FakeConnection.peer = peer
                with self.assertRaises(Failure) as caught:
                    jev.post("http://localhost:8649/v1/systemone", b"{}", "key-marker", 10)
                self.assertEqual(caught.exception.code, "invalid_input")
                self.assertNotIn("key-marker", str(caught.exception))
                [connection] = FakeConnection.made
                self.assertEqual(connection.requests, [])
                self.assertTrue(connection.closed)

    def test_on_this_mac(self) -> None:
        for peer in ("127.0.0.1", "127.8.9.10", "::1", "::ffff:127.0.0.1"):
            self.assertTrue(jev.on_this_mac(peer), peer)
        for peer in ("192.168.1.20", "0.0.0.0", "::", "::ffff:10.0.0.1", "fe80::1%lo0", "localhost", ""):
            self.assertFalse(jev.on_this_mac(peer), peer)

    def test_a_call_that_cannot_be_made(self) -> None:
        # One attempt and a first mapping; the table of errors and the attempts come with SYL-162.
        for error, code in (
            (TimeoutError(), "limit_reached"),
            (ConnectionRefusedError(), "vendor_unavailable"),
            (http.client.RemoteDisconnected("closed"), "vendor_unavailable"),
            (http.client.BadStatusLine("x"), "vendor_error"),
        ):
            with self.subTest(error=error):
                FakeConnection.fail = error
                with self.assertRaises(Failure) as caught:
                    jev.post("http://127.0.0.1:9/v1/systemone", b"{}", "key-marker", 10)
                self.assertEqual(caught.exception.code, code)
                self.assertNotIn("key-marker", str(caught.exception))
