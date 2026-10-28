"""One attempt at Jev, with a fake connection: only the endpoint's address, the key as a bearer token, and an
attempt that cannot outlast the time limit of the call (CLS-0.5, 0.9, 0.13)."""

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

# TEST-TIER-DISABLED-BEGIN tests/test_jev.py::Transport.test_the_body_goes_to_the_endpoint_with_the_key_as_a_bearer_token
#     def test_the_body_goes_to_the_endpoint_with_the_key_as_a_bearer_token(self) -> None:
#         FakeConnection.peer = "203.0.113.7"
#         status, answer, retry_after = jev.post("https://api.typesafe.ai/v1/systemone", b'{"state":"x"}', "key-marker",
#                                                Deadline(7.5))
#         self.assertEqual((status, answer, retry_after), (200, b'{"answer": true}', None))
#         [connection] = FakeConnection.made
#         self.assertEqual((connection.host, connection.port), ("api.typesafe.ai", None))
#         self.assertTrue(7 < connection.timeout <= 7.5, connection.timeout)
#         self.assertIsNotNone(connection.context)
#         self.assertEqual(
#             connection.requests,
#             [("POST", "/v1/systemone", b'{"state":"x"}', {"Authorization": "Bearer key-marker",
#                                                           "Content-Type": "application/json",
#                                                           "User-Agent": "arbol-classifier"})],
#         )
#         self.assertTrue(connection.closed)
# TEST-TIER-DISABLED-END tests/test_jev.py::Transport.test_the_body_goes_to_the_endpoint_with_the_key_as_a_bearer_token

# TEST-TIER-DISABLED-BEGIN tests/test_jev.py::Transport.test_an_address_on_this_mac
#     def test_an_address_on_this_mac(self) -> None:
#         for endpoint, peer, host, port, path in (
#             ("http://127.0.0.1:8649/v1/systemone", "127.0.0.1", "127.0.0.1", 8649, "/v1/systemone"),
#             ("http://localhost:9/x?y=1", "::1", "localhost", 9, "/x?y=1"),
#             ("https://[::1]:7000/v1/systemone", "::1", "::1", 7000, "/v1/systemone"),
#             ("http://localhost", "::ffff:127.0.0.1", "localhost", None, "/"),
#         ):
#             with self.subTest(endpoint=endpoint):
#                 FakeConnection.made = []
#                 FakeConnection.peer = peer
#                 jev.post(endpoint, b"{}", "key", Deadline(10))
#                 [connection] = FakeConnection.made
#                 self.assertEqual((connection.host, connection.port, connection.requests[0][1]), (host, port, path))
# TEST-TIER-DISABLED-END tests/test_jev.py::Transport.test_an_address_on_this_mac

# TEST-TIER-DISABLED-BEGIN tests/test_jev.py::Transport.test_an_endpoint_on_this_mac_that_leads_elsewhere_is_refused_before_anything_is_sent
#     def test_an_endpoint_on_this_mac_that_leads_elsewhere_is_refused_before_anything_is_sent(self) -> None:
#         for peer in ("192.168.1.20", "203.0.113.7", "::ffff:192.168.1.20", "fe80::1%en0", ""):
#             with self.subTest(peer=peer):
#                 FakeConnection.made = []
#                 FakeConnection.peer = peer
#                 with self.assertRaises(Failure) as caught:
#                     jev.post("http://localhost:8649/v1/systemone", b"{}", "key-marker", Deadline(10))
#                 self.assertEqual(caught.exception.code, "invalid_input")
#                 self.assertNotIn("key-marker", str(caught.exception))
#                 [connection] = FakeConnection.made
#                 self.assertEqual(connection.requests, [])
#                 self.assertTrue(connection.closed)
# TEST-TIER-DISABLED-END tests/test_jev.py::Transport.test_an_endpoint_on_this_mac_that_leads_elsewhere_is_refused_before_anything_is_sent

# TEST-TIER-DISABLED-BEGIN tests/test_jev.py::Transport.test_on_this_mac
#     def test_on_this_mac(self) -> None:
#         for peer in ("127.0.0.1", "127.8.9.10", "::1", "::ffff:127.0.0.1"):
#             self.assertTrue(jev.on_this_mac(peer), peer)
#         for peer in ("192.168.1.20", "0.0.0.0", "::", "::ffff:10.0.0.1", "fe80::1%lo0", "localhost", ""):
#             self.assertFalse(jev.on_this_mac(peer), peer)
# TEST-TIER-DISABLED-END tests/test_jev.py::Transport.test_on_this_mac

# TEST-TIER-DISABLED-BEGIN tests/test_jev.py::Transport.test_an_attempt_that_cannot_be_made
#     def test_an_attempt_that_cannot_be_made(self) -> None:
#         # A failed connection is vendor_unavailable, which classify tries again (CLS-0.11).
#         for error, code in (
#             (TimeoutError(), "limit_reached"),
#             (ConnectionRefusedError(), "vendor_unavailable"),
#             (http.client.RemoteDisconnected("closed"), "vendor_unavailable"),
#             (http.client.BadStatusLine("x"), "vendor_error"),
#         ):
#             with self.subTest(error=error):
#                 FakeConnection.fail = error
#                 with self.assertRaises(Failure) as caught:
#                     jev.post("http://127.0.0.1:9/v1/systemone", b"{}", "key-marker", Deadline(10))
#                 self.assertEqual(caught.exception.code, code)
#                 self.assertNotIn("key-marker", str(caught.exception))
# TEST-TIER-DISABLED-END tests/test_jev.py::Transport.test_an_attempt_that_cannot_be_made

# TEST-TIER-DISABLED-BEGIN tests/test_jev.py::Transport.test_an_attempt_ends_with_the_time_limit_of_the_call
#     def test_an_attempt_ends_with_the_time_limit_of_the_call(self) -> None:
#         FakeResponse.slow = 3.0
#         started = time.monotonic()
#         with patch("arbol_classifier.limits.SCALE", 0.1), self.assertRaises(Failure) as caught:
#             jev.post("http://127.0.0.1:9/v1/systemone", b"{}", "key-marker", Deadline(2))
#         self.assertLess(time.monotonic() - started, 1.0)
#         self.assertEqual(caught.exception.code, "limit_reached")
#         self.assertIn("2 seconds", str(caught.exception))
# TEST-TIER-DISABLED-END tests/test_jev.py::Transport.test_an_attempt_ends_with_the_time_limit_of_the_call

# TEST-TIER-DISABLED-BEGIN tests/test_jev.py::Transport.test_retry_after_in_seconds
#     def test_retry_after_in_seconds(self) -> None:
#         for header, expected in (("7", 7), (" 120 ", 120), ("Wed, 21 Oct 2026 07:28:00 GMT", None), ("-1", None),
#                                  ("1.5", None), (None, None)):
#             with self.subTest(header=header):
#                 FakeResponse.retry_after = header
#                 self.assertEqual(jev.post("http://127.0.0.1:9/v1/systemone", b"{}", "key", Deadline(10))[2], expected)
# TEST-TIER-DISABLED-END tests/test_jev.py::Transport.test_retry_after_in_seconds

# Archived complete imports; restore needed names in their original scope, not at this file tail.
# TEST-TIER-IMPORTS-BEGIN tests/test_jev.py:10
# from arbol_classifier import jev
# TEST-TIER-IMPORTS-END tests/test_jev.py:10
# TEST-TIER-IMPORTS-BEGIN tests/test_jev.py:11
# from arbol_classifier.errors import Failure
# TEST-TIER-IMPORTS-END tests/test_jev.py:11
# TEST-TIER-IMPORTS-BEGIN tests/test_jev.py:12
# from arbol_classifier.limits import Deadline
# TEST-TIER-IMPORTS-END tests/test_jev.py:12
