"""Individually selected top-tier cases. Shared fixtures retain their original paths."""
from __future__ import annotations

import test_key as _support
from test_key import (
    ACCOUNT,
    Deadline,
    FILE,
    FIND,
    SERVICE,
    Settings,
    json,
    read_key,
    store_key,
)


class StoreKey(_support.StoreKey):
    def test_the_key_goes_to_security_on_standard_input_never_as_an_argument(self) -> None:
        self.assertFalse(store_key("key-marker-new"))
        self.assertEqual(self.security.value(SERVICE, ACCOUNT), "key-marker-new")
        calls = self.security.calls()
        self.assertEqual(
            [call["args"] for call in calls], [["find-generic-password", "-s", SERVICE, "-a", ACCOUNT], ["-i"], FIND]
        )
        self.assertIn("key-marker-new", calls[1]["stdin"])
        for call in calls:
            self.assertNotIn("key-marker", json.dumps(call["args"]) + json.dumps(call["env"]))
        self.assertEqual(read_key(Settings(), FILE, Deadline(10)), "key-marker-new")
