"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_terminal as _support
from test_terminal import (PROMPT ,os ,read_hidden ,shown_until ,termios ,threading)


class Terminal(_support.Terminal):
# TEST-TIER-BEGIN tests/test_terminal.py::Terminal.test_the_key_is_read_with_echo_off_and_the_terminal_is_set_back
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
# TEST-TIER-END tests/test_terminal.py::Terminal.test_the_key_is_read_with_echo_off_and_the_terminal_is_set_back

# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: tests/mid/test_mid_terminal.py::Terminal.test_an_empty_line_and_the_end_of_input
# Reason: Empty-input or no-terminal behavior is represented by the real executable refusal/lifecycle checks; only the direct PTY echo/restoration observation adds separate information. Case reviewed: An empty line and the end of input.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_terminal.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_terminal.py::NoTerminal.test_without_a_terminal_add_key_refuses
# Reason: Empty-input or no-terminal behavior is represented by the real executable refusal/lifecycle checks; only the direct PTY echo/restoration observation adds separate information. Case reviewed: Without a terminal add key refuses.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_terminal.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END
