
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: tests/test_arguments.py::Arguments.test_commands_and_their_options
# Reason: Copies ordinary valid argument records and default values; execution adds little beyond the parser.
# Source: arbol-classifier@acd8ffd6bd645e443ccce2b3ba8b4befd2e75173:tests/test_arguments.py
# Retained evidence at review: Actual info/classify CLI dispatch plus duplicate-option and numeric-boundary refusal cases remain.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_commands_and_their_options(self) -> None:
#         self.assertEqual(parse_arguments(["info"]), Command("info"))
#         self.assertEqual(parse_arguments(["info", "--settings", "a.json"]), Command("info", None, "a.json"))
#         self.assertEqual(parse_arguments(["--settings=a.json", "info"]), Command("info", None, "a.json"))
#         self.assertEqual(parse_arguments(["classify"]), Command("classify"))
#         self.assertEqual(parse_arguments(["classify", "--timeout", "5"]), Command("classify", 5.0))
#         self.assertEqual(
#             parse_arguments(["classify", "--timeout=2.5", "--settings", "b.json"]), Command("classify", 2.5, "b.json")
#         )
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/test_arguments.py::Arguments.test_timeout_belongs_to_classify_only
# Reason: Single assertion repeats the command-options membership table for info.
# Source: arbol-classifier@acd8ffd6bd645e443ccce2b3ba8b4befd2e75173:tests/test_arguments.py
# Retained evidence at review: Unknown/duplicate/missing options and bounded numeric timeout cases remain.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_timeout_belongs_to_classify_only(self) -> None:
#         self.assertIn("--timeout", str(self.refused("info", "--timeout", "5")))
# LOW-TIER-SOURCE-END
# LOW-TIER-END
