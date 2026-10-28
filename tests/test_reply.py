"""Jev's reply: the model asked for, an answer for every question and no other, and nothing taken away (CLS-0.6, 0.7)."""

import json
import unittest

from arbol_classifier.errors import Failure
from arbol_classifier.reply import accept_reply

ANSWER = {"type": "noul", "noul": 0.5}


def reply(value: object) -> bytes:
    return json.dumps(value).encode("utf-8")


class Replies(unittest.TestCase):
    def refused(self, data: bytes, asked: tuple[str, ...] = ("work",), model: str = "jev-1.13.0") -> Failure:
        with self.assertRaises(Failure) as caught:
            accept_reply(data, model, asked)
        self.assertEqual(caught.exception.code, "vendor_error")
        return caught.exception

# TEST-TIER-DISABLED-BEGIN tests/test_reply.py::Replies.test_the_reply_is_given_as_jev_gave_it
#     def test_the_reply_is_given_as_jev_gave_it(self) -> None:
#         value = {
#             "model": "jev-1.13.0",
#             "answers": {"work": ANSWER, "kind": {"type": "choice", "choice": "a", "extra": [1, None]}},
#             "usage": {"input_tokens": 212, "output_tokens": 30},
#             "id": "a field the classifier does not know",
#         }
#         self.assertEqual(accept_reply(reply(value), "jev-1.13.0", ["work", "kind"]), value)
# TEST-TIER-DISABLED-END tests/test_reply.py::Replies.test_the_reply_is_given_as_jev_gave_it

# TEST-TIER-DISABLED-BEGIN tests/test_reply.py::Replies.test_a_reply_from_another_model_fails
#     def test_a_reply_from_another_model_fails(self) -> None:
#         for model in ("jev-1.14.0", "jev-latest", None, ["jev-1.13.0"]):
#             failure = self.refused(reply({"model": model, "answers": {"work": ANSWER}}))
#             self.assertIn("jev-1.13.0", str(failure))
#         self.refused(reply({"answers": {"work": ANSWER}}))
#         self.assertEqual(accept_reply(reply({"model": "jev-1.14.0", "answers": {"work": ANSWER}}), "jev-1.14.0",
#                                       ["work"])["model"], "jev-1.14.0")
# TEST-TIER-DISABLED-END tests/test_reply.py::Replies.test_a_reply_from_another_model_fails

# TEST-TIER-DISABLED-BEGIN tests/test_reply.py::Replies.test_every_question_asked_has_an_answer_and_no_other_has
#     def test_every_question_asked_has_an_answer_and_no_other_has(self) -> None:
#         self.assertIn("lacks", str(self.refused(reply({"model": "jev-1.13.0", "answers": {"work": ANSWER}}),
#                                                 ("work", "polite"))))
#         self.assertIn("not asked", str(self.refused(reply({"model": "jev-1.13.0", "answers": {"work": ANSWER,
#                                                                                               "other": ANSWER}}))))
#         self.refused(reply({"model": "jev-1.13.0", "answers": {}}))
#         self.refused(reply({"model": "jev-1.13.0"}))
#         self.refused(reply({"model": "jev-1.13.0", "answers": [ANSWER]}))
# TEST-TIER-DISABLED-END tests/test_reply.py::Replies.test_every_question_asked_has_an_answer_and_no_other_has

# TEST-TIER-DISABLED-BEGIN tests/test_reply.py::Replies.test_a_reply_that_is_not_json_fails
#     def test_a_reply_that_is_not_json_fails(self) -> None:
#         for data in (b"", b"not JSON", b"\xff", b"[]", b"null", b'{"model": NaN}', b"[" * 100000):
#             with self.subTest(data=data[:20]):
#                 self.refused(data)
#         self.refused(b'{"model": "jev-1.13.0", "answers": {"work": "\\udc00"}}')
# TEST-TIER-DISABLED-END tests/test_reply.py::Replies.test_a_reply_that_is_not_json_fails
