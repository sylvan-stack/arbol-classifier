# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
"""The settings file: the defaults, every field of ClassifierSettings, and a faulty file refused."""

from arbol_classifier.settings import (
    DEFAULT_ENDPOINT,
    Settings,
    allowed_endpoint,
    exact_model,
    read_settings,
)


import json
import tempfile
import unittest
from pathlib import Path

from arbol_classifier.errors import Failure
from arbol_classifier.settings import (
    Settings,
    read_settings,
)


class SettingsFile(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="arbol-classifier-settings-")
        self.addCleanup(temporary.cleanup)
        self.file = Path(temporary.name) / "arbol-classifier.json"

    def read(self, value: object) -> Settings:
        self.file.write_text(value if isinstance(value, str) else json.dumps(value), encoding="utf-8")
        return read_settings(self.file)

    def refused(self, value: object, *names: str, hidden: str | None = None) -> Failure:
        with self.assertRaises(Failure) as caught:
            self.read(value)
        failure = caught.exception
        self.assertEqual(failure.code, "invalid_input")
        self.assertIn(str(self.file), str(failure))
        for name in names:
            self.assertIn(name, str(failure))
        if hidden is not None:
            self.assertNotIn(hidden, str(failure))
        return failure


class Addresses(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


# Archived complete imports; restore needed names in their original scope, not at this file tail.
