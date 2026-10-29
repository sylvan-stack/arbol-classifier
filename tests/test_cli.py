# Shared fixtures only; test bodies are in top/ and mid/. See TESTS.md.
"""One invocation: `info`, the refusals, and the error object of DRV-4 with the codes of CLS-0."""

import tempfile
import unittest
from pathlib import Path

from stand_ins import security_stand_in

ROOT = Path(__file__).resolve().parent.parent


class Invocation(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="arbol-classifier-cli-")
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.environ = {"HOME": str(self.home)}
        self.security = security_stand_in(self)


# Archived complete imports; restore needed names in their original scope, not at this file tail.
