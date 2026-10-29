"""Individually selected top-tier cases. Shared fixtures retain their original paths."""
from __future__ import annotations

import test_classify as _support
from test_classify import (
    FakeJev,
    failure_of,
    patch,
    time,
)


class Attempts(_support.Attempts):
    def test_no_wait_goes_past_the_time_limit(self) -> None:
        # Scaled by 0.1: a limit of 0.12 s holds the first wait of 0.05 s, not the second of 0.1 s.
        with patch("arbol_classifier.limits.SCALE", 0.1):
            started = time.monotonic()
            send = FakeJev(529)
            failure = failure_of(self, send, seconds=1.2)
        self.assertEqual((failure.code, len(send.calls)), ("vendor_unavailable", 2))
        self.assertLess(time.monotonic() - started, 0.12)
        self.assertIn("Attempts made: 2", str(failure))
