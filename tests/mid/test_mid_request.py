
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: tests/mid/test_mid_request.py::Requests.test_no_question_is_interpreted
# Reason: Repeats local request validation or serialization. The retained HTTP size-limit and wire scenarios provide independent received-byte evidence; these local variants add no distinct boundary failure. Case reviewed: No question is interpreted.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_request.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_no_question_is_interpreted(self) -> None:
#         # CLS-0.4: neither the type nor the criteria nor any other field of a question is judged.
#         for question in (
#             {"type": "rank", "instructions": "Order them"},
#             {"type": None, "instructions": None},
#             {"type": "choice", "instructions": [], "criteria": {}},
#             {"type": "score", "instructions": "How?", "criteria": ["only one level"], "hint": {"any": "data"}},
#             {"type": 5, "instructions": {"nested": [1, 2.5, None, True]}},
#         ):
#             with self.subTest(question=question):
#                 request = {"state": None, "questions": {"q": question}, "trace": {"kept": True}}
#                 self.assertEqual(read_request(encoded(request)), request)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_request.py::Requests.test_only_the_listed_checks
# Reason: Repeats local request validation or serialization. The retained HTTP size-limit and wire scenarios provide independent received-byte evidence; these local variants add no distinct boundary failure. Case reviewed: Only the listed checks.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_request.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_only_the_listed_checks(self) -> None:
#         # CLS-0: one JSON object, a state, at least one question, a type and instructions in each, no model.
#         self.refused(b"", "JSON")
#         self.refused(b"{", "JSON")
#         self.refused(b"{} {}", "JSON")
#         self.refused(b"\xff\xfe{}", "JSON")
#         self.refused(b'{"state": NaN, "questions": {}}', "JSON")
#         self.refused(b"[" * 100000, "JSON")
#         values: tuple[object, ...] = ([], "text", None, 5)
#         for value in values:
#             self.refused(encoded(value), "object")
#         self.refused(encoded({"questions": {"work": NOUL}}), "state")
#         faulty: tuple[object, ...] = (None, {}, [NOUL], "work")
#         for questions in faulty:
#             self.refused(encoded({"state": "x", "questions": questions}), "questions")
#         for question in ("Does it ask for work?", {"instructions": "x"}, {"type": "noul"}, None, [NOUL]):
#             self.refused(encoded({"state": "x", "questions": {"work": NOUL, "other": question}}), "type", "instructions")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_request.py::Requests.test_a_request_that_names_a_model_is_refused
# Reason: Repeats local request validation or serialization. The retained HTTP size-limit and wire scenarios provide independent received-byte evidence; these local variants add no distinct boundary failure. Case reviewed: A request that names a model is refused.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_request.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_request_that_names_a_model_is_refused(self) -> None:
#         for model in ("jev-1.13.0", "jev-latest", None, ["jev-1.13.0"]):
#             failure = self.refused(encoded({"state": "x", "questions": {"work": NOUL}, "model": model}), "model")
#             self.assertNotIn("jev-latest", str(failure))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_request.py::Requests.test_the_judged_text_is_in_no_message
# Reason: Repeats local request validation or serialization. The retained HTTP size-limit and wire scenarios provide independent received-byte evidence; these local variants add no distinct boundary failure. Case reviewed: The judged text is in no message.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_request.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_judged_text_is_in_no_message(self) -> None:
#         for request in ({"state": "judged marker"}, {"state": "judged marker", "questions": {"q": "judged marker"}}):
#             self.assertNotIn("judged marker", str(self.refused(encoded(request))))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_request.py::SizeLimit.test_the_limit_is_measured_on_the_body_as_it_is_sent
# Reason: Repeats local request validation or serialization. The retained HTTP size-limit and wire scenarios provide independent received-byte evidence; these local variants add no distinct boundary failure. Case reviewed: The limit is measured on the body as it is sent.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_request.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_limit_is_measured_on_the_body_as_it_is_sent(self) -> None:
#         size = len(body_for_jev(self.request, "jev-1.13.0", 64000))
#         self.assertEqual(body_for_jev(self.request, "jev-1.13.0", size), body_for_jev(self.request, "jev-1.13.0", 64000))
#         with self.assertRaises(Failure) as caught:
#             body_for_jev(self.request, "jev-1.13.0", size - 1)
#         self.assertEqual(caught.exception.code, "invalid_input")
#         self.assertIn(str(size), str(caught.exception))
#         self.assertIn(str(size - 1), str(caught.exception))
#         # A longer model name makes the body longer: the limit counts what is sent, model included.
#         with self.assertRaises(Failure):
#             body_for_jev(self.request, "jev-10.13.0", size)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_request.py::SizeLimit.test_text_is_counted_in_bytes_of_utf_8
# Reason: Repeats local request validation or serialization. The retained HTTP size-limit and wire scenarios provide independent received-byte evidence; these local variants add no distinct boundary failure. Case reviewed: Text is counted in bytes of utf 8.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_request.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_text_is_counted_in_bytes_of_utf_8(self) -> None:
#         request: dict[str, Json] = {"state": "ñ" * 100, "questions": {"work": dict(NOUL)}}
#         size = len(body_for_jev(request, "jev-1.13.0", 64000))
#         self.assertEqual(size, len(body_for_jev({**request, "state": "n" * 100}, "jev-1.13.0", 64000)) + 100)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_request.py::SizeLimit.test_nothing_is_cut
# Reason: Repeats local request validation or serialization. The retained HTTP size-limit and wire scenarios provide independent received-byte evidence; these local variants add no distinct boundary failure. Case reviewed: Nothing is cut.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_request.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_nothing_is_cut(self) -> None:
#         request: dict[str, Json] = {"state": "x" * 63800, "questions": {"work": dict(NOUL)}}
#         body = body_for_jev(request, "jev-1.13.0", 64000)
#         self.assertEqual(loads(body.decode("utf-8")), {**request, "model": "jev-1.13.0"})
#         with self.assertRaises(Failure) as caught:
#             body_for_jev({**request, "state": "x" * 64000}, "jev-1.13.0", 64000)
#         self.assertIn("Nothing was sent", str(caught.exception))
#         self.assertNotIn("xxxx", str(caught.exception))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_request.py::SizeLimit.test_a_body_that_cannot_be_sent_is_refused
# Reason: Repeats local request validation or serialization. The retained HTTP size-limit and wire scenarios provide independent received-byte evidence; these local variants add no distinct boundary failure. Case reviewed: A body that cannot be sent is refused.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_request.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_body_that_cannot_be_sent_is_refused(self) -> None:
#         for data in (b'{"state": 1e400, "questions": {"q": {"type": "noul", "instructions": "x"}}}',
#                      b'{"state": "\\ud800", "questions": {"q": {"type": "noul", "instructions": "x"}}}'):
#             with self.subTest(data=data), self.assertRaises(Failure) as caught:
#                 body_for_jev(read_request(data), "jev-1.13.0", 64000)
#             self.assertEqual(caught.exception.code, "invalid_input")
# LOW-TIER-SOURCE-END
# LOW-TIER-END
