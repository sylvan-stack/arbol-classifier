
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: tests/test_identity.py::Identity.test_the_record_in_the_builds_own_folder
# Reason: Writes a valid record and checks two fields are returned unchanged.
# Source: arbol-classifier@acd8ffd6bd645e443ccce2b3ba8b4befd2e75173:tests/test_identity.py
# Retained evidence at review: Damaged/cross-product identity refusal and actual info/build-record integration remain.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_record_in_the_builds_own_folder(self) -> None:
#         self.record({"component": "arbol-classifier", "build": "a3", "packageVersion": "1.0.0", "status": "building"})
#         self.assertEqual(build_identity(self.module), ("1.0.0", "a3"))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/test_identity.py::Identity.test_outside_a_build_the_build_number_is_zero
# Reason: Checks the literal development fallback; expected_identity duplicates the same file-selection logic.
# Source: arbol-classifier@acd8ffd6bd645e443ccce2b3ba8b4befd2e75173:tests/test_identity.py
# Retained evidence at review: Actual info identity and malformed identity tests remain; expected_identity is kept where CLI tests use it.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_outside_a_build_the_build_number_is_zero(self) -> None:
#         self.assertEqual(build_identity(self.module), ("1.2.3", "0"))
#         self.assertEqual(build_identity(ROOT / "src/arbol_classifier"), expected_identity())
# LOW-TIER-SOURCE-END
# LOW-TIER-END
