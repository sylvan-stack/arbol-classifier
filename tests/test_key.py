"""The key from the command that the settings name; the Keychain comes with SYL-161."""

import sys
import tempfile
import unittest
from pathlib import Path

from arbol_classifier.errors import Failure
from arbol_classifier.key import read_key
from arbol_classifier.settings import Settings

FILE = Path("/Users/someone/.arbol/arbol-classifier.json")


def command(code: str) -> Settings:
    return Settings(secret_command=(sys.executable, "-I", "-B", "-c", code))


class KeyCommand(unittest.TestCase):
    def missing(self, settings: Settings, why: str, timeout: float = 10) -> Failure:
        with self.assertRaises(Failure) as caught:
            read_key(settings, FILE, timeout)
        failure = caught.exception
        self.assertEqual(failure.code, "not_signed_in")
        self.assertIn("No Jev API key was found", str(failure))
        self.assertIn(str(FILE), str(failure))
        self.assertIn(why, str(failure))
        self.assertIsNotNone(failure.remedy)
        self.assertNotIn("key-marker", str(failure) + str(failure.remedy))
        return failure

    def test_what_the_command_prints_is_the_key(self) -> None:
        self.assertEqual(read_key(command("print('key-marker-1')"), FILE, 10), "key-marker-1")
        self.assertEqual(read_key(command("print('  key-marker-2\\r\\n')"), FILE, 10), "key-marker-2")

    def test_a_command_that_fails_or_prints_nothing_gives_not_signed_in(self) -> None:
        self.missing(command("import sys; print('key-marker'); sys.exit(3)"), "failed")
        self.missing(command("pass"), "printed nothing")
        self.missing(command("print('   ')"), "printed nothing")
        self.missing(command("print('key-marker with space')"), "not a key")
        self.missing(command("print('key-marker\\nsecond line')"), "not a key")
        self.missing(command("import time; time.sleep(5)"), "did not end", timeout=0.5)
        with tempfile.TemporaryDirectory() as name:
            self.missing(Settings(secret_command=(str(Path(name) / "no-such-program"),)), "could not be started")

    def test_the_keychain_is_not_part_of_this_build_yet(self) -> None:
        with self.assertRaises(Failure) as caught:
            read_key(Settings(), FILE, 10)
        self.assertEqual(caught.exception.code, "internal")
