
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: tests/mid/test_mid_reply.py::Replies.test_the_reply_is_given_as_jev_gave_it
# Reason: Repeats local reply predicates or dictionary pass-through; retained real HTTP model and answer-integrity scenarios challenge the same failure mechanisms across the executable. Case reviewed: The reply is given as jev gave it.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_reply.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_reply_is_given_as_jev_gave_it(self) -> None:
#         value = {
#             "model": "jev-1.13.0",
#             "answers": {"work": ANSWER, "kind": {"type": "choice", "choice": "a", "extra": [1, None]}},
#             "usage": {"input_tokens": 212, "output_tokens": 30},
#             "id": "a field the classifier does not know",
#         }
#         self.assertEqual(accept_reply(reply(value), "jev-1.13.0", ["work", "kind"]), value)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_reply.py::Replies.test_a_reply_from_another_model_fails
# Reason: Repeats local reply predicates or dictionary pass-through; retained real HTTP model and answer-integrity scenarios challenge the same failure mechanisms across the executable. Case reviewed: A reply from another model fails.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_reply.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_reply_from_another_model_fails(self) -> None:
#         for model in ("jev-1.14.0", "jev-latest", None, ["jev-1.13.0"]):
#             failure = self.refused(reply({"model": model, "answers": {"work": ANSWER}}))
#             self.assertIn("jev-1.13.0", str(failure))
#         self.refused(reply({"answers": {"work": ANSWER}}))
#         self.assertEqual(accept_reply(reply({"model": "jev-1.14.0", "answers": {"work": ANSWER}}), "jev-1.14.0",
#                                       ["work"])["model"], "jev-1.14.0")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_reply.py::Replies.test_every_question_asked_has_an_answer_and_no_other_has
# Reason: Repeats local reply predicates or dictionary pass-through; retained real HTTP model and answer-integrity scenarios challenge the same failure mechanisms across the executable. Case reviewed: Every question asked has an answer and no other has.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_reply.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_every_question_asked_has_an_answer_and_no_other_has(self) -> None:
#         self.assertIn("lacks", str(self.refused(reply({"model": "jev-1.13.0", "answers": {"work": ANSWER}}),
#                                                 ("work", "polite"))))
#         self.assertIn("not asked", str(self.refused(reply({"model": "jev-1.13.0", "answers": {"work": ANSWER,
#                                                                                               "other": ANSWER}}))))
#         self.refused(reply({"model": "jev-1.13.0", "answers": {}}))
#         self.refused(reply({"model": "jev-1.13.0"}))
#         self.refused(reply({"model": "jev-1.13.0", "answers": [ANSWER]}))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_reply.py::Replies.test_a_reply_that_is_not_json_fails
# Reason: Repeats local reply predicates or dictionary pass-through; retained real HTTP model and answer-integrity scenarios challenge the same failure mechanisms across the executable. Case reviewed: A reply that is not json fails.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_reply.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_reply_that_is_not_json_fails(self) -> None:
#         for data in (b"", b"not JSON", b"\xff", b"[]", b"null", b'{"model": NaN}', b"[" * 100000):
#             with self.subTest(data=data[:20]):
#                 self.refused(data)
#         self.refused(b'{"model": "jev-1.13.0", "answers": {"work": "\\udc00"}}')
# LOW-TIER-SOURCE-END
# LOW-TIER-END
