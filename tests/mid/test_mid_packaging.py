"""Commented mid-tier selections; see MID_TIER.md before restoring a case."""

# Restore the needed imports and class header only for an explicit testing task.
# import test_packaging as _support
# from test_packaging import (
#     Packaging,
#     Path,
#     ROOT,
#     sys,
#     unittest,
# )


# class Packaging(_support.Packaging):
# TEST-TIER-DISABLED-BEGIN tests/test_packaging.py::Packaging.test_corrupted_cached_distribution_is_refused_without_a_download
#     def test_corrupted_cached_distribution_is_refused_without_a_download(self) -> None:
#         with tempfile.TemporaryDirectory() as name:
#             expected = hashlib.sha256(b"expected archive").hexdigest()
#             (Path(name) / f"{expected}.tar.gz").write_bytes(b"corrupt archive")
#             with (
#                 patch.dict(os.environ, {"ARBOL_PYTHON_ARCHIVE_CACHE": name}),
#                 patch("urllib.request.urlopen") as download,
#             ):
#                 with self.assertRaisesRegex(ValueError, "wrong SHA-256"):
#                     package_build.archive(
#                         {
#                             "url": "https://github.com/astral-sh/python-build-standalone/releases/download/t/p.tar.gz",
#                             "sha256": expected,
#                         }
#                     )
#                 download.assert_not_called()
# TEST-TIER-DISABLED-END tests/test_packaging.py::Packaging.test_corrupted_cached_distribution_is_refused_without_a_download

# TEST-TIER-DISABLED-BEGIN tests/test_packaging.py::Packaging.test_archive_pin_rejects_nonhex_digests_and_untrusted_sources
#     def test_archive_pin_rejects_nonhex_digests_and_untrusted_sources(self) -> None:
#         for distribution in (
#             {"url": "https://example.invalid/python.tar.gz", "sha256": "f" * 64},
#             {"url": "https://github.com/astral-sh/python-build-standalone/releases/download/t/p.tar.gz", "sha256": "/" * 64},
#         ):
#             with self.subTest(distribution=distribution), patch("urllib.request.urlopen") as download:
#                 with self.assertRaisesRegex(ValueError, "pinned URL and SHA-256"):
#                     package_build.archive(distribution)
#                 download.assert_not_called()
# TEST-TIER-DISABLED-END tests/test_packaging.py::Packaging.test_archive_pin_rejects_nonhex_digests_and_untrusted_sources

# TEST-TIER-DISABLED-BEGIN tests/test_packaging.py::Packaging.test_candidate_cannot_overwrite_a_numbered_build
#     def test_candidate_cannot_overwrite_a_numbered_build(self) -> None:
#         with tempfile.TemporaryDirectory() as name:
#             (Path(name) / "build.json").write_text("{}\n")
#             with self.assertRaisesRegex(ValueError, "cannot replace a numbered Build"):
#                 build_support.build_folder(name)
# TEST-TIER-DISABLED-END tests/test_packaging.py::Packaging.test_candidate_cannot_overwrite_a_numbered_build

# TEST-TIER-DISABLED-BEGIN tests/test_packaging.py::Packaging.test_build_record_requires_matching_number_entry_and_version
#     def test_build_record_requires_matching_number_entry_and_version(self) -> None:
#         with tempfile.TemporaryDirectory() as name:
#             folder = Path(name)
#             record = {"component": build_support.COMPONENT, "build": "a", "packageVersion": "1.0.0",
#                       "entry": build_support.ENTRY}
#             (folder / "build.json").write_text(json.dumps(record))
#             with (
#                 patch.dict(os.environ, {"ARBOL_BUILD_DIR": name, "ARBOL_BUILD_NUMBER": "b"}),
#                 patch.object(build_support, "metadata", return_value=("1.0.0", {})),
#             ):
#                 with self.assertRaisesRegex(ValueError, "must match this component"):
#                     build_support.build_folder()
#             with (
#                 patch.dict(os.environ, {"ARBOL_BUILD_DIR": name, "ARBOL_BUILD_NUMBER": "a"}),
#                 patch.object(build_support, "metadata", return_value=("1.0.0", {})),
#             ):
#                 self.assertEqual(build_support.build_folder(), (folder.resolve(), "a"))
#             for number in ("0", "0a", "A", ""):
#                 with patch.dict(os.environ, {"ARBOL_BUILD_DIR": name, "ARBOL_BUILD_NUMBER": number}):
#                     with self.assertRaisesRegex(ValueError, "lower-case hexadecimal"):
#                         build_support.build_folder()
# TEST-TIER-DISABLED-END tests/test_packaging.py::Packaging.test_build_record_requires_matching_number_entry_and_version


# Original deferred imports (restore at the required scope, never blindly at the tail).
# TEST-TIER-IMPORTS-BEGIN tests/test_packaging.py:5
# import hashlib
# TEST-TIER-IMPORTS-END tests/test_packaging.py:5

# TEST-TIER-IMPORTS-BEGIN tests/test_packaging.py:6
# import json
# TEST-TIER-IMPORTS-END tests/test_packaging.py:6

# TEST-TIER-IMPORTS-BEGIN tests/test_packaging.py:7
# import os
# TEST-TIER-IMPORTS-END tests/test_packaging.py:7

# TEST-TIER-IMPORTS-BEGIN tests/test_packaging.py:9
# import tempfile
# TEST-TIER-IMPORTS-END tests/test_packaging.py:9

# TEST-TIER-IMPORTS-BEGIN tests/test_packaging.py:12
# from unittest.mock import patch
# TEST-TIER-IMPORTS-END tests/test_packaging.py:12

# TEST-TIER-IMPORTS-BEGIN tests/test_packaging.py:15
# import build_support  # noqa: E402
# TEST-TIER-IMPORTS-END tests/test_packaging.py:15

# TEST-TIER-IMPORTS-BEGIN tests/test_packaging.py:16
# import package_build  # noqa: E402
# TEST-TIER-IMPORTS-END tests/test_packaging.py:16

raise RuntimeError("Mid-tier tests require an explicitly requested testing task; see MID_TIER.md.")
