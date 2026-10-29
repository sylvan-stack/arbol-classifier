# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
"""The request: only the checks CLS-0 lists (CLS-0.4), and the size limit on the body as it is sent (CLS-0.10)."""

from arbol_classifier.json_types import Json, loads
from arbol_classifier.request import body_for_jev, read_request


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


class SizeLimit(unittest.TestCase):
    request: dict[str, Json] = {"state": "Can you also update the README?", "questions": {"work": dict(NOUL)}}


# Archived complete imports; restore needed names in their original scope, not at this file tail.
