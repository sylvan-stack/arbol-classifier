# Shared fixtures only; test bodies are in top/ and mid/. See TESTS.md.
"""The key: from the Keychain item at each call, or from the command the settings name, and `add-key` (CLS-0.8, 0.16).

A stand-in takes the place of the system's `security` command; no test reaches the real Keychain.
"""

import json
import sys
import unittest
from pathlib import Path

from stand_ins import security_stand_in

from arbol_classifier.errors import Failure
from arbol_classifier.key import ACCOUNT, SERVICE, key_found, read_key, store_key
from arbol_classifier.limits import Deadline
from arbol_classifier.settings import Settings

FILE = Path("/Users/someone/.arbol/arbol-classifier.json")
NO_KEY = (
    "No Jev API key was found. arbol-classifier looked in the login Keychain for the item with the service "
    "com.sylvan-stack.arbol.classifier and the account jev."
)
FIND = ["find-generic-password", "-s", SERVICE, "-a", ACCOUNT, "-w"]


def command(code: str) -> Settings:
    return Settings(secret_command=(sys.executable, "-I", "-B", "-c", code))


def missing(test: unittest.TestCase, settings: Settings, *why: str) -> Failure:
    """The call ends with not_signed_in: no Jev API key was found, where it was looked for, and how to store it."""
    with test.assertRaises(Failure) as caught:
        read_key(settings, FILE, Deadline(10))
    failure = caught.exception
    test.assertEqual(failure.code, "not_signed_in")
    test.assertTrue(str(failure).startswith("No Jev API key was found."), str(failure))
    for part in why:
        test.assertIn(part, str(failure))
    test.assertIsNotNone(failure.remedy)
    test.assertIn("arbol-classifier add-key", str(failure.remedy))
    test.assertNotIn("key-marker", str(failure) + str(failure.remedy))
    test.assertFalse(key_found(settings, FILE, 10))
    return failure


def too_slow(test: unittest.TestCase, settings: Settings, during: str) -> None:
    """A key source that is still busy at the time limit of the call ends it with limit_reached (CLS-0.9)."""
    with test.assertRaises(Failure) as caught:
        read_key(settings, FILE, Deadline(0.5))
    test.assertEqual(caught.exception.code, "limit_reached")
    test.assertIn("0.5 seconds", str(caught.exception))
    test.assertIn(during, str(caught.exception))
    test.assertFalse(key_found(settings, FILE, 0.5))


class Keychain(unittest.TestCase):
    def setUp(self) -> None:
        self.security = security_stand_in(self)


class KeyCommand(unittest.TestCase):
    def setUp(self) -> None:
        self.security = security_stand_in(self)


class StoreKey(unittest.TestCase):
    def setUp(self) -> None:
        self.security = security_stand_in(self)


# Archived complete imports; restore needed names in their original scope, not at this file tail.
