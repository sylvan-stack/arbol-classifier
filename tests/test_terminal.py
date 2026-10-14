"""`add-key` asks at the terminal without showing what is typed, and refuses without a terminal (CLS-0.16)."""

import os
import select
import tempfile
import termios
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from arbol_classifier import terminal
from arbol_classifier.errors import Failure
from arbol_classifier.terminal import PROMPT, ask_for_key, read_hidden


def shown_until(master: int, text: bytes, seconds: float = 10) -> bytes:
    """What the terminal shows, read until `text` appears."""
    shown = b""
    end = time.monotonic() + seconds
    while text not in shown and time.monotonic() < end:
        ready, _, _ = select.select([master], [], [], 0.1)
        if ready:
            shown += os.read(master, 1024)
    return shown


class Terminal(unittest.TestCase):
    def setUp(self) -> None:
        self.master, self.slave = os.openpty()
        self.addCleanup(os.close, self.master)
        self.addCleanup(os.close, self.slave)

    def test_the_key_is_read_with_echo_off_and_the_terminal_is_set_back(self) -> None:
        before = termios.tcgetattr(self.slave)
        shown: list[bytes] = []

        def person() -> None:
            shown.append(shown_until(self.master, PROMPT.encode()))
            os.write(self.master, b"key-marker-typed\n")
            shown.append(shown_until(self.master, b"\n", 2))

        typing = threading.Thread(target=person)
        typing.start()
        line = read_hidden(self.slave, PROMPT)
        typing.join(10)
        self.assertEqual(line, "key-marker-typed\n")
        self.assertIn(PROMPT.encode(), shown[0])
        self.assertNotIn(b"key-marker", b"".join(shown))
        self.assertEqual(termios.tcgetattr(self.slave), before)

    def test_an_empty_line_and_the_end_of_input(self) -> None:
        def person(data: bytes) -> None:
            shown_until(self.master, PROMPT.encode())
            os.write(self.master, data)

        for data, expected in ((b"\n", "\n"), (b"\x04", "")):
            typing = threading.Thread(target=person, args=(data,))
            typing.start()
            self.assertEqual(read_hidden(self.slave, PROMPT), expected)
            typing.join(10)


class NoTerminal(unittest.TestCase):
    def test_without_a_terminal_add_key_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            plain = Path(name) / "not-a-terminal"
            plain.write_text("key-marker-in-a-file\n")
            for path in (Path(name) / "missing", plain):
                with self.subTest(path=path), patch.object(terminal, "TERMINAL", str(path)):
                    with self.assertRaises(Failure) as caught:
                        ask_for_key()
                    self.assertEqual(caught.exception.code, "invalid_input")
                    self.assertIn("at a terminal, and there is none", str(caught.exception))
                    self.assertNotIn("key-marker", str(caught.exception))
