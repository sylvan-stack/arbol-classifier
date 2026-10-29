
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: tests/test_request.py::Requests.test_the_three_kinds_are_accepted
# Reason: Parses an ordinary valid JSON request and reads its question keys back unchanged.
# Source: arbol-classifier@b512805acf6b277376abcb442fb430f814db0ae9:tests/test_request.py
# Retained evidence at review: Non-obvious pass-through of uninterpreted question types, malformed request and actual classification cases remain.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_three_kinds_are_accepted(self) -> None:
#         request = {
#             "state": "Can you also update the README?",
#             "questions": {
#                 "kind": {"type": "choice", "instructions": "What is it?", "criteria": {"request": "Work", "other": None}},
#                 "work": NOUL,
#                 "urgency": {"type": "score", "instructions": {"ask": "How urgent?"}, "criteria": ["Low", "High"]},
#             },
#         }
#         self.assertEqual(read_request(encoded(request)), request)
#         self.assertEqual(question_names(read_request(encoded(request))), ["kind", "work", "urgency"])
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/test_request.py::SizeLimit.test_the_body_is_the_request_with_the_model_added
# Reason: Expected value repeats the exact dictionary-unpack expression in body_for_jev.
# Source: arbol-classifier@b512805acf6b277376abcb442fb430f814db0ae9:tests/test_request.py
# Retained evidence at review: Actual classifier request construction and UTF-8/body-size boundary cases remain.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_body_is_the_request_with_the_model_added(self) -> None:
#         body = body_for_jev(self.request, "jev-1.13.0", 64000)
#         self.assertEqual(loads(body.decode("utf-8")), {**self.request, "model": "jev-1.13.0"})
# LOW-TIER-SOURCE-END
# LOW-TIER-END
