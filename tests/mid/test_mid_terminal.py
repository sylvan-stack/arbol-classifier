"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_terminal as _support
from test_terminal import (
    Failure,
    NoTerminal,
    PROMPT,
    Path,
    Terminal,
    ask_for_key,
    os,
    patch,
    read_hidden,
    select,
    shown_until,
    tempfile,
    terminal,
    termios,
    threading,
    time,
    unittest,
)


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

# TEST-TIER-BEGIN tests/test_terminal.py::Terminal.test_an_empty_line_and_the_end_of_input
    def test_an_empty_line_and_the_end_of_input(self) -> None:
        def person(data: bytes) -> None:
            shown_until(self.master, PROMPT.encode())
            os.write(self.master, data)

        for data, expected in ((b"\n", "\n"), (b"\x04", "")):
            typing = threading.Thread(target=person, args=(data,))
            typing.start()
            self.assertEqual(read_hidden(self.slave, PROMPT), expected)
            typing.join(10)
# TEST-TIER-END tests/test_terminal.py::Terminal.test_an_empty_line_and_the_end_of_input



class NoTerminal(_support.NoTerminal):
# TEST-TIER-BEGIN tests/test_terminal.py::NoTerminal.test_without_a_terminal_add_key_refuses
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
# TEST-TIER-END tests/test_terminal.py::NoTerminal.test_without_a_terminal_add_key_refuses
