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

# TEST-TIER-DISABLED-BEGIN tests/test_key.py::Keychain.test_the_key_is_read_from_the_item_at_each_call
#     def test_the_key_is_read_from_the_item_at_each_call(self) -> None:
#         self.security.put(SERVICE, ACCOUNT, "key-marker-1")
#         self.assertEqual(read_key(Settings(), FILE, Deadline(10)), "key-marker-1")
#         self.security.put(SERVICE, ACCOUNT, "key-marker-2")
#         self.assertEqual(read_key(Settings(), FILE, Deadline(10)), "key-marker-2")
#         self.assertTrue(key_found(Settings(), FILE, 10))
#         self.assertEqual([call["args"] for call in self.security.calls()], [FIND, FIND, FIND])
# TEST-TIER-DISABLED-END tests/test_key.py::Keychain.test_the_key_is_read_from_the_item_at_each_call

# TEST-TIER-DISABLED-BEGIN tests/test_key.py::Keychain.test_only_the_classifiers_own_item_is_read
#     def test_only_the_classifiers_own_item_is_read(self) -> None:
#         self.security.put(SERVICE, "other", "key-marker-other")
#         self.security.put("mycel", "jev-api-key", "key-marker-mycel")
#         missing(self, Settings(), str(SERVICE), str(ACCOUNT))
# TEST-TIER-DISABLED-END tests/test_key.py::Keychain.test_only_the_classifiers_own_item_is_read

# TEST-TIER-DISABLED-BEGIN tests/test_key.py::Keychain.test_no_item
#     def test_no_item(self) -> None:
#         failure = missing(self, Settings())
#         self.assertEqual(str(failure), NO_KEY)
#         self.assertEqual(failure.remedy, "Store the key with: arbol-classifier add-key")
# TEST-TIER-DISABLED-END tests/test_key.py::Keychain.test_no_item

# TEST-TIER-DISABLED-BEGIN tests/test_key.py::Keychain.test_an_empty_item
#     def test_an_empty_item(self) -> None:
#         self.security.put(SERVICE, ACCOUNT, "")
#         failure = missing(self, Settings(), "the service com.sylvan-stack.arbol.classifier and the account jev",
#                           "the item is empty")
#         self.assertEqual(failure.remedy, "Store the key with: arbol-classifier add-key")
#         self.security.put(SERVICE, ACCOUNT, "  ")
#         missing(self, Settings(), "the item is empty")
# TEST-TIER-DISABLED-END tests/test_key.py::Keychain.test_an_empty_item

# TEST-TIER-DISABLED-BEGIN tests/test_key.py::Keychain.test_an_item_that_cannot_be_a_key
#     def test_an_item_that_cannot_be_a_key(self) -> None:
#         for value in ("key-marker with space", "key-marker\nsecond line", "key-markeré"):
#             self.security.put(SERVICE, ACCOUNT, value)
#             missing(self, Settings(), "cannot be a key")
# TEST-TIER-DISABLED-END tests/test_key.py::Keychain.test_an_item_that_cannot_be_a_key

# TEST-TIER-DISABLED-BEGIN tests/test_key.py::Keychain.test_an_item_that_cannot_be_read
#     def test_an_item_that_cannot_be_read(self) -> None:
#         self.security.put(SERVICE, ACCOUNT, "key-marker")
#         self.security.fail(51)
#         missing(self, Settings(), "could not be read", "status 51")
# TEST-TIER-DISABLED-END tests/test_key.py::Keychain.test_an_item_that_cannot_be_read

# TEST-TIER-DISABLED-BEGIN tests/test_key.py::Keychain.test_security_that_cannot_be_started_or_does_not_answer
#     def test_security_that_cannot_be_started_or_does_not_answer(self) -> None:
#         with tempfile.TemporaryDirectory() as name:
#             with patch.object(key_module, "SECURITY", str(Path(name) / "no-such-program")):
#                 missing(self, Settings(), "could not be started")
#             slow = Path(name) / "security"
#             slow.write_text("#!/bin/sh\nsleep 5\n")
#             slow.chmod(0o755)
#             with patch.object(key_module, "SECURITY", str(slow)):
#                 too_slow(self, Settings(), "while the Jev API key was read from the login Keychain")
# TEST-TIER-DISABLED-END tests/test_key.py::Keychain.test_security_that_cannot_be_started_or_does_not_answer

# TEST-TIER-DISABLED-BEGIN tests/test_key.py::Keychain.test_a_key_command_in_the_settings_takes_the_place_of_the_item
#     def test_a_key_command_in_the_settings_takes_the_place_of_the_item(self) -> None:
#         self.security.put(SERVICE, ACCOUNT, "key-marker-item")
#         self.assertEqual(read_key(command("print('key-marker-command')"), FILE, Deadline(10)), "key-marker-command")
#         self.assertEqual(self.security.calls(), [])
# TEST-TIER-DISABLED-END tests/test_key.py::Keychain.test_a_key_command_in_the_settings_takes_the_place_of_the_item


class KeyCommand(unittest.TestCase):
    def setUp(self) -> None:
        self.security = security_stand_in(self)

# TEST-TIER-DISABLED-BEGIN tests/test_key.py::KeyCommand.test_what_the_command_prints_is_the_key
#     def test_what_the_command_prints_is_the_key(self) -> None:
#         self.assertEqual(read_key(command("print('key-marker-1')"), FILE, Deadline(10)), "key-marker-1")
#         self.assertEqual(read_key(command("print('  key-marker-2\\r\\n')"), FILE, Deadline(10)), "key-marker-2")
# TEST-TIER-DISABLED-END tests/test_key.py::KeyCommand.test_what_the_command_prints_is_the_key

# TEST-TIER-DISABLED-BEGIN tests/test_key.py::KeyCommand.test_a_command_that_fails_or_prints_nothing_gives_not_signed_in
#     def test_a_command_that_fails_or_prints_nothing_gives_not_signed_in(self) -> None:
#         where = f"the command that the settings file {FILE} names for the key"
#         missing(self, command("import sys; print('key-marker'); sys.exit(3)"), where, "failed")
#         missing(self, command("pass"), where, "printed nothing")
#         missing(self, command("print('   ')"), "printed nothing")
#         missing(self, command("print('key-marker with space')"), "not a key")
#         missing(self, command("print('key-marker\\nsecond line')"), "not a key")
#         too_slow(self, command("import time; time.sleep(5)"), f"while the command that the settings file {FILE} names")
#         with tempfile.TemporaryDirectory() as name:
#             missing(self, Settings(secret_command=(str(Path(name) / "no-such-program"),)), "could not be started")
#         self.assertEqual(self.security.calls(), [])
# TEST-TIER-DISABLED-END tests/test_key.py::KeyCommand.test_a_command_that_fails_or_prints_nothing_gives_not_signed_in


class StoreKey(unittest.TestCase):
    def setUp(self) -> None:
        self.security = security_stand_in(self)

    def test_the_key_goes_to_security_on_standard_input_never_as_an_argument(self) -> None:
        self.assertFalse(store_key("key-marker-new"))
        self.assertEqual(self.security.value(SERVICE, ACCOUNT), "key-marker-new")
        calls = self.security.calls()
        self.assertEqual(
            [call["args"] for call in calls], [["find-generic-password", "-s", SERVICE, "-a", ACCOUNT], ["-i"], FIND]
        )
        self.assertIn("key-marker-new", calls[1]["stdin"])
        for call in calls:
            self.assertNotIn("key-marker", json.dumps(call["args"]) + json.dumps(call["env"]))
        self.assertEqual(read_key(Settings(), FILE, Deadline(10)), "key-marker-new")

# TEST-TIER-DISABLED-BEGIN tests/test_key.py::StoreKey.test_a_key_stored_before_is_replaced
#     def test_a_key_stored_before_is_replaced(self) -> None:
#         self.security.put(SERVICE, ACCOUNT, "key-marker-old")
#         self.assertTrue(store_key("key-marker-second"))
#         self.assertEqual(self.security.value(SERVICE, ACCOUNT), "key-marker-second")
# TEST-TIER-DISABLED-END tests/test_key.py::StoreKey.test_a_key_stored_before_is_replaced

# TEST-TIER-DISABLED-BEGIN tests/test_key.py::StoreKey.test_every_visible_character_reaches_the_item_unchanged
#     def test_every_visible_character_reaches_the_item_unchanged(self) -> None:
#         for key in ('key"marker\\with\\"quotes', "key'marker$`!#;%&*(){}[]<>|~^?=+,.:@", "-w", '\\"'):
#             store_key(key)
#             self.assertEqual(self.security.value(SERVICE, ACCOUNT), key)
# TEST-TIER-DISABLED-END tests/test_key.py::StoreKey.test_every_visible_character_reaches_the_item_unchanged

# TEST-TIER-DISABLED-BEGIN tests/test_key.py::StoreKey.test_only_a_key_that_can_be_one_is_stored
#     def test_only_a_key_that_can_be_one_is_stored(self) -> None:
#         for key in ("", "key-marker with space", "key-marker\nadd-generic-password -s x -a y -w z"):
#             with self.assertRaises(ValueError):
#                 store_key(key)
#         self.assertEqual(self.security.calls(), [])
# TEST-TIER-DISABLED-END tests/test_key.py::StoreKey.test_only_a_key_that_can_be_one_is_stored

# TEST-TIER-DISABLED-BEGIN tests/test_key.py::StoreKey.test_a_keychain_that_does_not_store_the_key_ends_with_internal
#     def test_a_keychain_that_does_not_store_the_key_ends_with_internal(self) -> None:
#         self.security.fail(51)
#         with self.assertRaises(Failure) as caught:
#             store_key("key-marker")
#         self.assertEqual(caught.exception.code, "internal")
#         self.assertIn("could not be stored", str(caught.exception))
#         self.assertNotIn("key-marker", str(caught.exception))
# TEST-TIER-DISABLED-END tests/test_key.py::StoreKey.test_a_keychain_that_does_not_store_the_key_ends_with_internal

# TEST-TIER-DISABLED-BEGIN tests/test_key.py::StoreKey.test_the_item_is_never_removed
#     def test_the_item_is_never_removed(self) -> None:
#         self.security.put(SERVICE, ACCOUNT, "key-marker-old")
#         store_key("key-marker-new")
#         read_key(Settings(), FILE, Deadline(10))
#         missing(self, command("pass"))
#         commands = [call["args"][0] for call in self.security.calls()] + [
#             word for call in self.security.calls() for word in call["stdin"].split()
#         ]
#         self.assertNotIn("delete-generic-password", commands)
# TEST-TIER-DISABLED-END tests/test_key.py::StoreKey.test_the_item_is_never_removed

# Archived complete imports; restore needed names in their original scope, not at this file tail.
# TEST-TIER-IMPORTS-BEGIN tests/test_key.py:8
# import tempfile
# TEST-TIER-IMPORTS-END tests/test_key.py:8
# TEST-TIER-IMPORTS-BEGIN tests/test_key.py:11
# from unittest.mock import patch
# TEST-TIER-IMPORTS-END tests/test_key.py:11
# TEST-TIER-IMPORTS-BEGIN tests/test_key.py:15
# from arbol_classifier import key as key_module
# TEST-TIER-IMPORTS-END tests/test_key.py:15
