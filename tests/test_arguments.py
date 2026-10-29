# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
"""The command line: one command, its options, and every other argument refused."""


import unittest

from arbol_classifier.arguments import parse_arguments
from arbol_classifier.errors import Failure


class Arguments(unittest.TestCase):
    def refused(self, *args: str) -> Failure:
        with self.assertRaises(Failure) as caught:
            parse_arguments(list(args))
        self.assertEqual(caught.exception.code, "invalid_input")
        return caught.exception
