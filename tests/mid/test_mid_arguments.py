
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: tests/mid/test_mid_arguments.py::Arguments.test_timeout_takes_one_to_sixty_seconds
# Reason: Routine parser acceptance/refusal permutations are visible in argument validation and add no distinct integration evidence beyond the retained real CLI workflows. Case reviewed: Timeout takes one to sixty seconds.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_arguments.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_timeout_takes_one_to_sixty_seconds(self) -> None:
#         for text, expected in (("1", 1.0), ("60", 60.0), ("10.25", 10.25), ("060", 60.0)):
#             with self.subTest(text=text):
#                 self.assertEqual(parse_arguments(["classify", "--timeout", text]).timeout_seconds, expected)
#         for text in ("0", "0.99", "60.01", "61", "-5", "ten", "1e1", " 5", "5 ", "５", "inf", "nan", "5."):
#             with self.subTest(text=text):
#                 self.assertIn("--timeout", str(self.refused("classify", "--timeout", text)))
#                 self.assertIn("--timeout", str(self.refused("classify", f"--timeout={text}")))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_arguments.py::Arguments.test_missing_and_unknown_commands
# Reason: Routine parser acceptance/refusal permutations are visible in argument validation and add no distinct integration evidence beyond the retained real CLI workflows. Case reviewed: Missing and unknown commands.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_arguments.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_missing_and_unknown_commands(self) -> None:
#         self.refused()
#         self.refused("--settings", "a.json")
#         failure = self.refused("judge-this-marker")
#         self.assertNotIn("judge-this-marker", str(failure))
#         self.refused("Info")
#         self.refused("info", "extra")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_arguments.py::Arguments.test_unknown_options_and_build_selection
# Reason: Routine parser acceptance/refusal permutations are visible in argument validation and add no distinct integration evidence beyond the retained real CLI workflows. Case reviewed: Unknown options and build selection.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_arguments.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_unknown_options_and_build_selection(self) -> None:
#         for args in (
#             ("info", "--verbose"),
#             ("info", "--state-dir", "/tmp"),
#             ("info", "-h"),
#             ("info", "--"),
#             ("-v", "3", "info"),
#             ("info", "-v", "3"),
#         ):
#             with self.subTest(args=args):
#                 self.refused(*args)
#         self.assertNotIn("secret-marker", str(self.refused("--key=secret-marker", "info")))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_arguments.py::Arguments.test_option_values_are_required_and_given_once
# Reason: Routine parser acceptance/refusal permutations are visible in argument validation and add no distinct integration evidence beyond the retained real CLI workflows. Case reviewed: Option values are required and given once.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_arguments.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_option_values_are_required_and_given_once(self) -> None:
#         self.refused("info", "--settings")
#         self.refused("info", "--settings=")
#         self.refused("info", "--settings", "--settings")
#         self.refused("classify", "--timeout")
#         self.refused("info", "--settings", "a", "--settings", "b")
#         self.refused("classify", "--timeout", "5", "--timeout=6")
# LOW-TIER-SOURCE-END
# LOW-TIER-END
