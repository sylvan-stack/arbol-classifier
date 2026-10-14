"""Delivery boundaries: the pinned archive, the Build record, the description and the checks."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_support  # noqa: E402
import check_build  # noqa: E402
import contract_checks  # noqa: E402
import package_build  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


class Packaging(unittest.TestCase):
    def test_corrupted_cached_distribution_is_refused_without_a_download(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            expected = hashlib.sha256(b"expected archive").hexdigest()
            (Path(name) / f"{expected}.tar.gz").write_bytes(b"corrupt archive")
            with (
                patch.dict(os.environ, {"ARBOL_PYTHON_ARCHIVE_CACHE": name}),
                patch("urllib.request.urlopen") as download,
            ):
                with self.assertRaisesRegex(ValueError, "wrong SHA-256"):
                    package_build.archive(
                        {
                            "url": "https://github.com/astral-sh/python-build-standalone/releases/download/t/p.tar.gz",
                            "sha256": expected,
                        }
                    )
                download.assert_not_called()

    def test_archive_pin_rejects_nonhex_digests_and_untrusted_sources(self) -> None:
        for distribution in (
            {"url": "https://example.invalid/python.tar.gz", "sha256": "f" * 64},
            {"url": "https://github.com/astral-sh/python-build-standalone/releases/download/t/p.tar.gz", "sha256": "/" * 64},
        ):
            with self.subTest(distribution=distribution), patch("urllib.request.urlopen") as download:
                with self.assertRaisesRegex(ValueError, "pinned URL and SHA-256"):
                    package_build.archive(distribution)
                download.assert_not_called()

    def test_package_metadata_must_agree(self) -> None:
        version, pin = build_support.metadata(ROOT)
        self.assertEqual(version, json.loads((ROOT / "package.json").read_text())["version"])
        self.assertEqual(pin["version"], (ROOT / ".python-version").read_text().strip())
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "pyproject.toml").write_text(
                f'[project]\nname = "{build_support.COMPONENT}"\nversion = "1.0.0"\ndependencies = []\n'
            )
            (root / "package.json").write_text('{"version":"9.0.0"}\n')
            with self.assertRaisesRegex(ValueError, "agree on the package version"):
                build_support.metadata(root)

    def test_candidate_cannot_overwrite_a_numbered_build(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            (Path(name) / "build.json").write_text("{}\n")
            with self.assertRaisesRegex(ValueError, "cannot replace a numbered Build"):
                build_support.build_folder(name)

    def test_build_record_requires_matching_number_entry_and_version(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            record = {"component": build_support.COMPONENT, "build": "a", "packageVersion": "1.0.0",
                      "entry": build_support.ENTRY}
            (folder / "build.json").write_text(json.dumps(record))
            with (
                patch.dict(os.environ, {"ARBOL_BUILD_DIR": name, "ARBOL_BUILD_NUMBER": "b"}),
                patch.object(build_support, "metadata", return_value=("1.0.0", {})),
            ):
                with self.assertRaisesRegex(ValueError, "must match this component"):
                    build_support.build_folder()
            with (
                patch.dict(os.environ, {"ARBOL_BUILD_DIR": name, "ARBOL_BUILD_NUMBER": "a"}),
                patch.object(build_support, "metadata", return_value=("1.0.0", {})),
            ):
                self.assertEqual(build_support.build_folder(), (folder.resolve(), "a"))
            for number in ("0", "0a", "A", ""):
                with patch.dict(os.environ, {"ARBOL_BUILD_DIR": name, "ARBOL_BUILD_NUMBER": number}):
                    with self.assertRaisesRegex(ValueError, "lower-case hexadecimal"):
                        build_support.build_folder()

    def test_the_description_names_the_three_checks(self) -> None:
        description = json.loads((ROOT / "arbol-build.json").read_text())
        self.assertEqual(description["component"], "arbol-classifier")
        self.assertEqual(description["entry"], build_support.ENTRY)
        self.assertEqual([check["kind"] for check in description["checks"]], ["unit", "contract", "live"])
        self.assertEqual([check["name"] for check in description["checks"]], ["unit", "contract", "live"])
        for check in description["checks"]:
            self.assertTrue(check["command"].endswith(f'/scripts/check_build.py" {check["kind"]}'))
            self.assertIn("-I -B", check["command"])

    def test_live_check_does_not_exist_yet(self) -> None:
        with patch("sys.stderr"):
            self.assertEqual(check_build.live(ROOT, None), 1)

    def test_the_contract_check_has_its_scenarios(self) -> None:
        names = [name for name, _ in contract_checks.SCENARIOS]
        self.assertEqual(len(names), len(set(names)))
        for name in ("info.identity", "info.defaults", "settings.unknown-key", "cli.unknown-command", "classify.choice",
                     "classify.noul", "classify.score", "classify.what-is-sent", "classify.names-a-model",
                     "classify.size-limit", "classify.other-model", "classify.missing-answer",
                     "classify.endpoint-elsewhere", "classify.writes-nothing", "key.keychain", "key.not-found",
                     "key.only-in-the-bearer-token", "add-key.at-a-terminal", "add-key.no-terminal",
                     "add-key.not-a-key", "add-key.keychain-refuses", "cli.add-key-arguments", "cli.build-entry",
                     "errors.credential-rejected", "errors.invalid-at-jev", "errors.rate-limited",
                     "errors.vendor-unavailable", "errors.vendor-error", "attempts.until-an-answer", "attempts.waits",
                     "limits.no-wait-past-the-limit", "limits.time-limit"):
            self.assertIn(name, names)
