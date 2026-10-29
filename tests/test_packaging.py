# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
"""Delivery boundaries: the pinned archive, the Build record, the description and the checks."""

from __future__ import annotations
import hashlib
import json
import os
import tempfile
from unittest.mock import patch


import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_support  # noqa: E402
import package_build  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]


class Packaging(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


# Archived complete imports; restore needed names in their original scope, not at this file tail.

# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: tests/test_packaging.py::Packaging.test_the_live_check_is_the_one_real_question
# Reason: Mocks the only delegated function and verifies its fixed return and forwarding argument.
# Source: arbol-classifier@1dfee903bbb88a6f8d95da33ed5a80e507de21f0:tests/test_packaging.py
# Retained evidence at review: tests/test_live.py exercises the real live-check orchestration using a private executable fixture.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_live_check_is_the_one_real_question(self) -> None:
#         with patch("live_check.run_live", return_value=0) as run_live:
#             self.assertEqual(check_build.live(ROOT, "5"), 0)
#         run_live.assert_called_once_with(ROOT)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/test_packaging.py::Packaging.test_the_contract_check_has_its_scenarios
# Reason: Duplicates the scenario-name registry without exercising any scenario or checking its quality.
# Source: arbol-classifier@1dfee903bbb88a6f8d95da33ed5a80e507de21f0:tests/test_packaging.py
# Retained evidence at review: scripts/contract_checks.py retains all executable contract scenarios for a requested testing task.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_contract_check_has_its_scenarios(self) -> None:
#         names = [name for name, _ in contract_checks.SCENARIOS]
#         self.assertEqual(len(names), len(set(names)))
#         for name in ("info.identity", "info.defaults", "settings.unknown-key", "cli.unknown-command", "classify.choice",
#                      "classify.noul", "classify.score", "classify.what-is-sent", "classify.names-a-model",
#                      "classify.size-limit", "classify.other-model", "classify.missing-answer",
#                      "classify.endpoint-elsewhere", "classify.writes-nothing", "key.keychain", "key.not-found",
#                      "key.only-in-the-bearer-token", "add-key.at-a-terminal", "add-key.no-terminal",
#                      "add-key.not-a-key", "add-key.keychain-refuses", "cli.add-key-arguments", "cli.build-entry",
#                      "errors.credential-rejected", "errors.invalid-at-jev", "errors.rate-limited",
#                      "errors.vendor-unavailable", "errors.vendor-error", "attempts.until-an-answer", "attempts.waits",
#                      "limits.no-wait-past-the-limit", "limits.time-limit"):
#             self.assertIn(name, names)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/test_packaging.py::Packaging.test_the_description_names_the_three_checks
# Reason: Copies static descriptor names and shell-command spelling; package validation and the real gate tests are retained.
# Source: arbol-classifier@1dfee903bbb88a6f8d95da33ed5a80e507de21f0:tests/test_packaging.py
# Retained evidence at review: Candidate overwrite, archive-integrity and numbered-build identity checks; tests/test_live.py.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_description_names_the_three_checks(self) -> None:
#         description = json.loads((ROOT / "arbol-build.json").read_text())
#         self.assertEqual(description["component"], "arbol-classifier")
#         self.assertEqual(description["entry"], build_support.ENTRY)
#         self.assertEqual([check["kind"] for check in description["checks"]], ["unit", "contract", "live"])
#         self.assertEqual([check["name"] for check in description["checks"]], ["unit", "contract", "live"])
#         for check in description["checks"]:
#             self.assertTrue(check["command"].endswith(f'/scripts/check_build.py" {check["kind"]}'))
#             self.assertIn("-I -B", check["command"])
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/test_packaging.py::Packaging.test_package_metadata_must_agree
# Reason: Sets two version strings to unequal values and asserts the explicit equality guard; no package installation or compatibility boundary is exercised.
# Source: arbol-classifier@1dfee903bbb88a6f8d95da33ed5a80e507de21f0:tests/test_packaging.py
# Retained evidence at review: Archive-integrity and numbered-build identity/entry refusal tests remain.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_package_metadata_must_agree(self) -> None:
#         version, pin = build_support.metadata(ROOT)
#         self.assertEqual(version, json.loads((ROOT / "package.json").read_text())["version"])
#         self.assertEqual(pin["version"], (ROOT / ".python-version").read_text().strip())
#         with tempfile.TemporaryDirectory() as name:
#             root = Path(name)
#             (root / "pyproject.toml").write_text(
#                 f'[project]\nname = "{build_support.COMPONENT}"\nversion = "1.0.0"\ndependencies = []\n'
#             )
#             (root / "package.json").write_text('{"version":"9.0.0"}\n')
#             with self.assertRaisesRegex(ValueError, "agree on the package version"):
#                 build_support.metadata(root)
# LOW-TIER-SOURCE-END
# LOW-TIER-END
