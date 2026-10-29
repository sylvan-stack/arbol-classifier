"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_jev as _support
from test_jev import (Deadline ,Failure ,FakeConnection ,jev)


class Transport(_support.Transport):


# TEST-TIER-BEGIN tests/test_jev.py::Transport.test_an_endpoint_on_this_mac_that_leads_elsewhere_is_refused_before_anything_is_sent
    def test_an_endpoint_on_this_mac_that_leads_elsewhere_is_refused_before_anything_is_sent(self) -> None:
        for peer in ("192.168.1.20", "203.0.113.7", "::ffff:192.168.1.20", "fe80::1%en0", ""):
            with self.subTest(peer=peer):
                FakeConnection.made = []
                FakeConnection.peer = peer
                with self.assertRaises(Failure) as caught:
                    jev.post("http://localhost:8649/v1/systemone", b"{}", "key-marker", Deadline(10))
                self.assertEqual(caught.exception.code, "invalid_input")
                self.assertNotIn("key-marker", str(caught.exception))
                [connection] = FakeConnection.made
                self.assertEqual(connection.requests, [])
                self.assertTrue(connection.closed)
# TEST-TIER-END tests/test_jev.py::Transport.test_an_endpoint_on_this_mac_that_leads_elsewhere_is_refused_before_anything_is_sent
