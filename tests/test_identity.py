"""The Build that runs: the package version and the build number (BLD-0.12 and 0.14)."""

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


# TEST-TIER-DISABLED-BEGIN tests/test_identity.py::Identity.test_a_damaged_record_is_a_defect
#     def test_a_damaged_record_is_a_defect(self) -> None:
#         values: tuple[object, ...] = (
#             [],
#             {"component": "arbol-codex-driver", "build": "1", "packageVersion": "1.0.0"},
#             {"component": "arbol-classifier", "build": "0a", "packageVersion": "1.0.0"},
#             {"component": "arbol-classifier", "build": "A", "packageVersion": "1.0.0"},
#             {"component": "arbol-classifier", "build": 1, "packageVersion": "1.0.0"},
#             {"component": "arbol-classifier", "build": "1", "packageVersion": "one"},
#         )
#         for value in values:
#             with self.subTest(value=value):
#                 self.record(value)
#                 with self.assertRaises(Failure) as caught:
#                     build_identity(self.module)
#                 self.assertEqual(caught.exception.code, "internal")
#         (self.folder / "build.json").write_text("{")
#         with self.assertRaises(Failure):
#             build_identity(self.module)
# TEST-TIER-DISABLED-END tests/test_identity.py::Identity.test_a_damaged_record_is_a_defect

# TEST-TIER-DISABLED-BEGIN tests/test_identity.py::Identity.test_another_package_is_not_this_one
#     def test_another_package_is_not_this_one(self) -> None:
#         (self.folder / "pyproject.toml").write_text('[project]\nname = "arbol-codex-driver"\nversion = "1.0.0"\n')
#         with self.assertRaises(Failure) as caught:
#             build_identity(self.module)
#         self.assertEqual(caught.exception.code, "internal")
# TEST-TIER-DISABLED-END tests/test_identity.py::Identity.test_another_package_is_not_this_one

# Archived complete imports; restore needed names in their original scope, not at this file tail.
# TEST-TIER-IMPORTS-BEGIN tests/test_identity.py:8
# from arbol_classifier.build import build_identity
# TEST-TIER-IMPORTS-END tests/test_identity.py:8
# TEST-TIER-IMPORTS-BEGIN tests/test_identity.py:9
# from arbol_classifier.errors import Failure
# TEST-TIER-IMPORTS-END tests/test_identity.py:9
