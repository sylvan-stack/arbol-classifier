# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
"""The key: from the Keychain item at each call, or from the command the settings name, and `add-key` (CLS-0.8, 0.16).

A stand-in takes the place of the system's `security` command; no test reaches the real Keychain.
"""
import tempfile
from unittest.mock import patch

from arbol_classifier import key as key_module


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

# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: tests/test_key.py::SystemCommand.test_the_systems_security_command_and_the_item_of_cls_0
# Reason: Compares three imported constants with the same three source literals.
# Source: arbol-classifier@1d77a9f4a205228e6b856f5ff4602a05511a1480:tests/test_key.py
# Retained evidence at review: Keychain and StoreKey behavioral cases inspect the actual security invocation and account isolation.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_systems_security_command_and_the_item_of_cls_0(self) -> None:
#         self.assertEqual(
#             (key_module.SECURITY, SERVICE, ACCOUNT), ("/usr/bin/security", "com.sylvan-stack.arbol.classifier", "jev")
#         )
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/test_key.py::KeyCommand.test_the_remedy_says_how_to_store_the_key
# Reason: Copies the full remedy sentence without exercising a distinct failure; the missing helper already checks the add-key remedy.
# Source: arbol-classifier@1d77a9f4a205228e6b856f5ff4602a05511a1480:tests/test_key.py
# Retained evidence at review: test_a_command_that_fails_or_prints_nothing_gives_not_signed_in and missing retain the failure and actionable remedy checks.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_remedy_says_how_to_store_the_key(self) -> None:
#         failure = missing(self, command("pass"))
#         self.assertEqual(
#             failure.remedy,
#             f"Correct secret.command in the settings file {FILE}, or remove secret from it and store the key with: "
#             "arbol-classifier add-key",
#         )
# LOW-TIER-SOURCE-END
# LOW-TIER-END
