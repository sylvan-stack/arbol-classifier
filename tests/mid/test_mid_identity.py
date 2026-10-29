"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_identity as _support
from test_identity import (
    Failure,
    Identity,
    Path,
    ROOT,
    build_identity,
    expected_identity,
    json,
    tempfile,
    unittest,
)


class Identity(_support.Identity):
# TEST-TIER-BEGIN tests/test_identity.py::Identity.test_a_damaged_record_is_a_defect
    def test_a_damaged_record_is_a_defect(self) -> None:
        values: tuple[object, ...] = (
            [],
            {"component": "arbol-codex-driver", "build": "1", "packageVersion": "1.0.0"},
            {"component": "arbol-classifier", "build": "0a", "packageVersion": "1.0.0"},
            {"component": "arbol-classifier", "build": "A", "packageVersion": "1.0.0"},
            {"component": "arbol-classifier", "build": 1, "packageVersion": "1.0.0"},
            {"component": "arbol-classifier", "build": "1", "packageVersion": "one"},
        )
        for value in values:
            with self.subTest(value=value):
                self.record(value)
                with self.assertRaises(Failure) as caught:
                    build_identity(self.module)
                self.assertEqual(caught.exception.code, "internal")
        (self.folder / "build.json").write_text("{")
        with self.assertRaises(Failure):
            build_identity(self.module)
# TEST-TIER-END tests/test_identity.py::Identity.test_a_damaged_record_is_a_defect

# TEST-TIER-BEGIN tests/test_identity.py::Identity.test_another_package_is_not_this_one
    def test_another_package_is_not_this_one(self) -> None:
        (self.folder / "pyproject.toml").write_text('[project]\nname = "arbol-codex-driver"\nversion = "1.0.0"\n')
        with self.assertRaises(Failure) as caught:
            build_identity(self.module)
        self.assertEqual(caught.exception.code, "internal")
# TEST-TIER-END tests/test_identity.py::Identity.test_another_package_is_not_this_one
