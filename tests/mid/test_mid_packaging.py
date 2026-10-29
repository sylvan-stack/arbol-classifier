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
