"""The request: only the checks CLS-0 lists (CLS-0.4), and the size limit on the body as it is sent (CLS-0.10)."""

import json
import unittest

from arbol_classifier.errors import Failure
from arbol_classifier.json_types import Json
from arbol_classifier.request import read_request

NOUL = {"type": "noul", "instructions": "Does it ask for work?"}


def encoded(value: object) -> bytes:
    return json.dumps(value).encode("utf-8")


class Requests(unittest.TestCase):
    def refused(self, data: bytes, *names: str) -> Failure:
        with self.assertRaises(Failure) as caught:
            read_request(data)
        self.assertEqual(caught.exception.code, "invalid_input")
        for name in names:
            self.assertIn(name, str(caught.exception))
        return caught.exception


# TEST-TIER-DISABLED-BEGIN tests/test_request.py::Requests.test_no_question_is_interpreted
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
# TEST-TIER-DISABLED-END tests/test_request.py::Requests.test_no_question_is_interpreted

# TEST-TIER-DISABLED-BEGIN tests/test_request.py::Requests.test_only_the_listed_checks
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
# TEST-TIER-DISABLED-END tests/test_request.py::Requests.test_only_the_listed_checks

# TEST-TIER-DISABLED-BEGIN tests/test_request.py::Requests.test_a_request_that_names_a_model_is_refused
#     def test_a_request_that_names_a_model_is_refused(self) -> None:
#         for model in ("jev-1.13.0", "jev-latest", None, ["jev-1.13.0"]):
#             failure = self.refused(encoded({"state": "x", "questions": {"work": NOUL}, "model": model}), "model")
#             self.assertNotIn("jev-latest", str(failure))
# TEST-TIER-DISABLED-END tests/test_request.py::Requests.test_a_request_that_names_a_model_is_refused

# TEST-TIER-DISABLED-BEGIN tests/test_request.py::Requests.test_the_judged_text_is_in_no_message
#     def test_the_judged_text_is_in_no_message(self) -> None:
#         for request in ({"state": "judged marker"}, {"state": "judged marker", "questions": {"q": "judged marker"}}):
#             self.assertNotIn("judged marker", str(self.refused(encoded(request))))
# TEST-TIER-DISABLED-END tests/test_request.py::Requests.test_the_judged_text_is_in_no_message


class SizeLimit(unittest.TestCase):
    request: dict[str, Json] = {"state": "Can you also update the README?", "questions": {"work": dict(NOUL)}}


# TEST-TIER-DISABLED-BEGIN tests/test_request.py::SizeLimit.test_the_limit_is_measured_on_the_body_as_it_is_sent
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
# TEST-TIER-DISABLED-END tests/test_request.py::SizeLimit.test_the_limit_is_measured_on_the_body_as_it_is_sent

# TEST-TIER-DISABLED-BEGIN tests/test_request.py::SizeLimit.test_text_is_counted_in_bytes_of_utf_8
#     def test_text_is_counted_in_bytes_of_utf_8(self) -> None:
#         request: dict[str, Json] = {"state": "ñ" * 100, "questions": {"work": dict(NOUL)}}
#         size = len(body_for_jev(request, "jev-1.13.0", 64000))
#         self.assertEqual(size, len(body_for_jev({**request, "state": "n" * 100}, "jev-1.13.0", 64000)) + 100)
# TEST-TIER-DISABLED-END tests/test_request.py::SizeLimit.test_text_is_counted_in_bytes_of_utf_8

# TEST-TIER-DISABLED-BEGIN tests/test_request.py::SizeLimit.test_nothing_is_cut
#     def test_nothing_is_cut(self) -> None:
#         request: dict[str, Json] = {"state": "x" * 63800, "questions": {"work": dict(NOUL)}}
#         body = body_for_jev(request, "jev-1.13.0", 64000)
#         self.assertEqual(loads(body.decode("utf-8")), {**request, "model": "jev-1.13.0"})
#         with self.assertRaises(Failure) as caught:
#             body_for_jev({**request, "state": "x" * 64000}, "jev-1.13.0", 64000)
#         self.assertIn("Nothing was sent", str(caught.exception))
#         self.assertNotIn("xxxx", str(caught.exception))
# TEST-TIER-DISABLED-END tests/test_request.py::SizeLimit.test_nothing_is_cut

# TEST-TIER-DISABLED-BEGIN tests/test_request.py::SizeLimit.test_a_body_that_cannot_be_sent_is_refused
#     def test_a_body_that_cannot_be_sent_is_refused(self) -> None:
#         for data in (b'{"state": 1e400, "questions": {"q": {"type": "noul", "instructions": "x"}}}',
#                      b'{"state": "\\ud800", "questions": {"q": {"type": "noul", "instructions": "x"}}}'):
#             with self.subTest(data=data), self.assertRaises(Failure) as caught:
#                 body_for_jev(read_request(data), "jev-1.13.0", 64000)
#             self.assertEqual(caught.exception.code, "invalid_input")
# TEST-TIER-DISABLED-END tests/test_request.py::SizeLimit.test_a_body_that_cannot_be_sent_is_refused

# Archived complete imports; restore needed names in their original scope, not at this file tail.
# TEST-TIER-IMPORTS-BEGIN tests/test_request.py:7
# from arbol_classifier.json_types import Json, loads
# TEST-TIER-IMPORTS-END tests/test_request.py:7
# TEST-TIER-IMPORTS-BEGIN tests/test_request.py:8
# from arbol_classifier.request import body_for_jev, read_request
# TEST-TIER-IMPORTS-END tests/test_request.py:8
