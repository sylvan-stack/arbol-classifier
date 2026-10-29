# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
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
