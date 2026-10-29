
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: tests/test_cli.py::Errors.test_the_eight_codes
# Reason: Copies error-enum cardinality, retry membership and envelope keys from the error wrapper.
# Source: arbol-classifier@1d77a9f4a205228e6b856f5ff4602a05511a1480:tests/test_cli.py
# Retained evidence at review: Actual failures through CLI, retry scheduling and secret-redaction cases remain.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_eight_codes(self) -> None:
#         self.assertEqual(len(CODES), 8)
#         for code in CODES:
#             error = Failure(code, "message").error()
#             self.assertEqual(error["retryable"], code in ("rate_limited", "vendor_unavailable"))
#             self.assertEqual(set(error), {"code", "message", "retryable"})
#         self.assertEqual(Failure("not_signed_in", "No key.", "Store the key.").error()["remedy"], "Store the key.")
#         for code in ("unsupported", "tool_missing", "state_newer", "not_found"):
#             with self.assertRaises(ValueError):
#                 Failure(code, "message")
# LOW-TIER-SOURCE-END
# LOW-TIER-END
