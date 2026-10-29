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
