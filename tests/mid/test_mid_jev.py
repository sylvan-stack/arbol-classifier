"""Commented mid-tier selections; see MID_TIER.md before restoring a case."""

# Restore the needed imports and class header only for an explicit testing task.
# import test_jev as _support
# from test_jev import (
#     Any,
#     FakeConnection,
#     FakeResponse,
#     FakeSocket,
#     Transport,
#     http,
#     patch,
#     time,
#     unittest,
# )


# class Transport(_support.Transport):
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


# Original deferred imports (restore at the required scope, never blindly at the tail).
# TEST-TIER-IMPORTS-BEGIN tests/test_jev.py:10
# from arbol_classifier import jev
# TEST-TIER-IMPORTS-END tests/test_jev.py:10

# TEST-TIER-IMPORTS-BEGIN tests/test_jev.py:11
# from arbol_classifier.errors import Failure
# TEST-TIER-IMPORTS-END tests/test_jev.py:11

# TEST-TIER-IMPORTS-BEGIN tests/test_jev.py:12
# from arbol_classifier.limits import Deadline
# TEST-TIER-IMPORTS-END tests/test_jev.py:12

raise RuntimeError("Mid-tier tests require an explicitly requested testing task; see MID_TIER.md.")
