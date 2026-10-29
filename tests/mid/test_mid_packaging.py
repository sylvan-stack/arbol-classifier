"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_packaging as _support
from test_packaging import (Path ,hashlib ,os ,package_build ,patch ,tempfile)


class Packaging(_support.Packaging):
# TEST-TIER-BEGIN tests/test_packaging.py::Packaging.test_corrupted_cached_distribution_is_refused_without_a_download
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
# TEST-TIER-END tests/test_packaging.py::Packaging.test_corrupted_cached_distribution_is_refused_without_a_download

# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: tests/mid/test_mid_packaging.py::Packaging.test_archive_pin_rejects_nonhex_digests_and_untrusted_sources
# Reason: Checks straightforward pin/metadata/number predicates with constructed values. Existing package verification retains those gates; only the corrupted-cache boundary adds distinct filesystem/network evidence. Case reviewed: Archive pin rejects nonhex digests and untrusted sources.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_packaging.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_archive_pin_rejects_nonhex_digests_and_untrusted_sources(self) -> None:
#         for distribution in (
#             {"url": "https://example.invalid/python.tar.gz", "sha256": "f" * 64},
#             {"url": "https://github.com/astral-sh/python-build-standalone/releases/download/t/p.tar.gz", "sha256": "/" * 64},
#         ):
#             with self.subTest(distribution=distribution), patch("urllib.request.urlopen") as download:
#                 with self.assertRaisesRegex(ValueError, "pinned URL and SHA-256"):
#                     package_build.archive(distribution)
#                 download.assert_not_called()
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_packaging.py::Packaging.test_candidate_cannot_overwrite_a_numbered_build
# Reason: Checks straightforward pin/metadata/number predicates with constructed values. Existing package verification retains those gates; only the corrupted-cache boundary adds distinct filesystem/network evidence. Case reviewed: Candidate cannot overwrite a numbered build.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_packaging.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_candidate_cannot_overwrite_a_numbered_build(self) -> None:
#         with tempfile.TemporaryDirectory() as name:
#             (Path(name) / "build.json").write_text("{}\n")
#             with self.assertRaisesRegex(ValueError, "cannot replace a numbered Build"):
#                 build_support.build_folder(name)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_packaging.py::Packaging.test_build_record_requires_matching_number_entry_and_version
# Reason: Checks straightforward pin/metadata/number predicates with constructed values. Existing package verification retains those gates; only the corrupted-cache boundary adds distinct filesystem/network evidence. Case reviewed: Build record requires matching number entry and version.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_packaging.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END
