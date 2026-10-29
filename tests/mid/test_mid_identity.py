"""Commented mid-tier selections; see MID_TIER.md before restoring a case."""

# Restore the needed imports and class header only for an explicit testing task.
# import test_identity as _support
# from test_identity import (
#     Identity,
#     Path,
#     ROOT,
#     expected_identity,
#     json,
#     tempfile,
#     unittest,
# )


# class Identity(_support.Identity):
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


# Original deferred imports (restore at the required scope, never blindly at the tail).
# TEST-TIER-IMPORTS-BEGIN tests/test_identity.py:8
# from arbol_classifier.build import build_identity
# TEST-TIER-IMPORTS-END tests/test_identity.py:8

# TEST-TIER-IMPORTS-BEGIN tests/test_identity.py:9
# from arbol_classifier.errors import Failure
# TEST-TIER-IMPORTS-END tests/test_identity.py:9

raise RuntimeError("Mid-tier tests require an explicitly requested testing task; see MID_TIER.md.")
