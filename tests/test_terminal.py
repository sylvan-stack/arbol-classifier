# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
"""`add-key` asks at the terminal without showing what is typed, and refuses without a terminal (CLS-0.16)."""
import tempfile
import termios
import threading
from pathlib import Path
from unittest.mock import patch

from arbol_classifier import terminal
from arbol_classifier.errors import Failure
from arbol_classifier.terminal import PROMPT, ask_for_key, read_hidden


import os
import select
import time
import unittest


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


class NoTerminal(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.

# Archived complete imports; restore needed names in their original scope, not at this file tail.
