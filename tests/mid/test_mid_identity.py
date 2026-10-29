
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: tests/mid/test_mid_identity.py::Identity.test_a_damaged_record_is_a_defect
# Reason: Constructs local metadata variants and repeats direct identity predicates; retained candidate identity and package verification observe the executable and manifest boundary. Case reviewed: A damaged record is a defect.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_identity.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_identity.py::Identity.test_another_package_is_not_this_one
# Reason: Constructs local metadata variants and repeats direct identity predicates; retained candidate identity and package verification observe the executable and manifest boundary. Case reviewed: Another package is not this one.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_identity.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_another_package_is_not_this_one(self) -> None:
#         (self.folder / "pyproject.toml").write_text('[project]\nname = "arbol-codex-driver"\nversion = "1.0.0"\n')
#         with self.assertRaises(Failure) as caught:
#             build_identity(self.module)
#         self.assertEqual(caught.exception.code, "internal")
# LOW-TIER-SOURCE-END
# LOW-TIER-END
