"""Commented mid-tier selections; see MID_TIER.md before restoring a case."""

# Restore the needed imports and class header only for an explicit testing task.
# import test_terminal as _support
# from test_terminal import (
#     NoTerminal,
#     Terminal,
#     os,
#     select,
#     shown_until,
#     time,
#     unittest,
# )


# class Terminal(_support.Terminal):
# TEST-TIER-DISABLED-BEGIN tests/test_terminal.py::Terminal.test_the_key_is_read_with_echo_off_and_the_terminal_is_set_back
#     def test_the_key_is_read_with_echo_off_and_the_terminal_is_set_back(self) -> None:
#         before = termios.tcgetattr(self.slave)
#         shown: list[bytes] = []
#
#         def person() -> None:
#             shown.append(shown_until(self.master, PROMPT.encode()))
#             os.write(self.master, b"key-marker-typed\n")
#             shown.append(shown_until(self.master, b"\n", 2))
#
#         typing = threading.Thread(target=person)
#         typing.start()
#         line = read_hidden(self.slave, PROMPT)
#         typing.join(10)
#         self.assertEqual(line, "key-marker-typed\n")
#         self.assertIn(PROMPT.encode(), shown[0])
#         self.assertNotIn(b"key-marker", b"".join(shown))
#         self.assertEqual(termios.tcgetattr(self.slave), before)
# TEST-TIER-DISABLED-END tests/test_terminal.py::Terminal.test_the_key_is_read_with_echo_off_and_the_terminal_is_set_back

# TEST-TIER-DISABLED-BEGIN tests/test_terminal.py::Terminal.test_an_empty_line_and_the_end_of_input
#     def test_an_empty_line_and_the_end_of_input(self) -> None:
#         def person(data: bytes) -> None:
#             shown_until(self.master, PROMPT.encode())
#             os.write(self.master, data)
#
#         for data, expected in ((b"\n", "\n"), (b"\x04", "")):
#             typing = threading.Thread(target=person, args=(data,))
#             typing.start()
#             self.assertEqual(read_hidden(self.slave, PROMPT), expected)
#             typing.join(10)
# TEST-TIER-DISABLED-END tests/test_terminal.py::Terminal.test_an_empty_line_and_the_end_of_input



# class NoTerminal(_support.NoTerminal):
# TEST-TIER-DISABLED-BEGIN tests/test_terminal.py::NoTerminal.test_without_a_terminal_add_key_refuses
#     def test_without_a_terminal_add_key_refuses(self) -> None:
#         with tempfile.TemporaryDirectory() as name:
#             plain = Path(name) / "not-a-terminal"
#             plain.write_text("key-marker-in-a-file\n")
#             for path in (Path(name) / "missing", plain):
#                 with self.subTest(path=path), patch.object(terminal, "TERMINAL", str(path)):
#                     with self.assertRaises(Failure) as caught:
#                         ask_for_key()
#                     self.assertEqual(caught.exception.code, "invalid_input")
#                     self.assertIn("at a terminal, and there is none", str(caught.exception))
#                     self.assertNotIn("key-marker", str(caught.exception))
# TEST-TIER-DISABLED-END tests/test_terminal.py::NoTerminal.test_without_a_terminal_add_key_refuses


# Original deferred imports (restore at the required scope, never blindly at the tail).
# TEST-TIER-IMPORTS-BEGIN tests/test_terminal.py:5
# import tempfile
# TEST-TIER-IMPORTS-END tests/test_terminal.py:5

# TEST-TIER-IMPORTS-BEGIN tests/test_terminal.py:6
# import termios
# TEST-TIER-IMPORTS-END tests/test_terminal.py:6

# TEST-TIER-IMPORTS-BEGIN tests/test_terminal.py:7
# import threading
# TEST-TIER-IMPORTS-END tests/test_terminal.py:7

# TEST-TIER-IMPORTS-BEGIN tests/test_terminal.py:10
# from pathlib import Path
# TEST-TIER-IMPORTS-END tests/test_terminal.py:10

# TEST-TIER-IMPORTS-BEGIN tests/test_terminal.py:11
# from unittest.mock import patch
# TEST-TIER-IMPORTS-END tests/test_terminal.py:11

# TEST-TIER-IMPORTS-BEGIN tests/test_terminal.py:13
# from arbol_classifier import terminal
# TEST-TIER-IMPORTS-END tests/test_terminal.py:13

# TEST-TIER-IMPORTS-BEGIN tests/test_terminal.py:14
# from arbol_classifier.errors import Failure
# TEST-TIER-IMPORTS-END tests/test_terminal.py:14

# TEST-TIER-IMPORTS-BEGIN tests/test_terminal.py:15
# from arbol_classifier.terminal import PROMPT, ask_for_key, read_hidden
# TEST-TIER-IMPORTS-END tests/test_terminal.py:15

raise RuntimeError("Mid-tier tests require an explicitly requested testing task; see MID_TIER.md.")
