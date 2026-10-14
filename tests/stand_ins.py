"""The stand-in for the system's `security` command in the unit tests, so that no test reaches the real Keychain."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from security_stand_in import SecurityStandIn  # noqa: E402

__all__ = ["SecurityStandIn", "security_stand_in"]


def security_stand_in(test: unittest.TestCase) -> SecurityStandIn:
    """A stand-in with an empty Keychain of its own, in place of `/usr/bin/security` until the test ends."""
    temporary = tempfile.TemporaryDirectory(prefix="arbol-classifier-security-")
    test.addCleanup(temporary.cleanup)
    stand_in = SecurityStandIn(Path(temporary.name))
    replacement = patch("arbol_classifier.key.SECURITY", str(stand_in.program))
    replacement.start()
    test.addCleanup(replacement.stop)
    return stand_in
