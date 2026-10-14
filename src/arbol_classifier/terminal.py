"""`add-key` asks the person at the terminal for the key, without showing it (CLS-0, CLS-D7).

The question goes to the terminal itself, `/dev/tty`, and never to standard input: a key is not
handed to the program. With no terminal to ask at, `add-key` refuses. Echo is off while the key
is typed, and the terminal is set back as it was afterwards.
"""

import os
import termios

from .errors import Failure

TERMINAL = "/dev/tty"
PROMPT = "Jev API key for arbol-classifier (it is not shown as you type): "
NOTHING_STORED = "Nothing was stored."


def read_hidden(fd: int, prompt: str) -> str:
    """Write the prompt to the terminal `fd` and read one line from it with echo off."""
    before = termios.tcgetattr(fd)
    hidden = list(before)
    hidden[3] = before[3] & ~termios.ECHO
    when = termios.TCSAFLUSH | getattr(termios, "TCSASOFT", 0)
    termios.tcsetattr(fd, when, hidden)
    try:
        os.write(fd, prompt.encode("utf-8"))
        data = b""
        while not data.endswith(b"\n"):
            chunk = os.read(fd, 1024)
            if not chunk:
                break
            data += chunk
    finally:
        termios.tcsetattr(fd, when, before)
        os.write(fd, b"\n")
    return data.decode("utf-8", "replace")


def ask_for_key() -> str:
    """The line the person typed at the terminal, or a refusal when there is no terminal."""
    no_terminal = Failure(
        "invalid_input",
        "add-key asks for the Jev API key at a terminal, and there is none. "
        f"Run arbol-classifier add-key in a terminal window. {NOTHING_STORED}",
    )
    try:
        fd = os.open(TERMINAL, os.O_RDWR | os.O_NOCTTY)
    except OSError:
        raise no_terminal from None
    try:
        return read_hidden(fd, PROMPT)
    except termios.error:
        raise no_terminal from None
    except KeyboardInterrupt:
        raise Failure("invalid_input", f"No key was typed. {NOTHING_STORED}") from None
    finally:
        os.close(fd)
