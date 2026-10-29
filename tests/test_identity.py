# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
"""The Build that runs: the package version and the build number (BLD-0.12 and 0.14)."""

from arbol_classifier.build import build_identity
from arbol_classifier.errors import Failure


import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def expected_identity() -> tuple[str, str]:
    """What the tests' own copy reports: a numbered Build's record, or the package version and Build 0."""
    record = ROOT / "build.json"
    if record.exists():
        value = json.loads(record.read_text())
        return str(value["packageVersion"]), str(value["build"])
    return str(json.loads((ROOT / "package.json").read_text())["version"]), "0"


class Identity(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="arbol-classifier-identity-")
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.module = self.folder / "src/arbol_classifier"
        self.module.mkdir(parents=True)
        (self.folder / "pyproject.toml").write_text('[project]\nname = "arbol-classifier"\nversion = "1.2.3"\n')

    def record(self, value: object) -> None:
        (self.folder / "build.json").write_text(json.dumps(value))


# Archived complete imports; restore needed names in their original scope, not at this file tail.
