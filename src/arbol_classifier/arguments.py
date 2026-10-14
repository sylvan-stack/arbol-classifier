"""The command line of CLS-0: one command, `--timeout` for `classify`, `--settings` for it and `info`."""

import math
import re
from dataclasses import dataclass

from .errors import Failure

COMMANDS: dict[str, tuple[str, ...]] = {"classify": ("timeout", "settings"), "info": ("settings",), "add-key": ()}
TIMEOUT_RANGE = (1.0, 60.0)
NUMBER = re.compile(r"[0-9]+(?:\.[0-9]+)?", re.ASCII)


@dataclass(frozen=True)
class Command:
    name: str
    timeout_seconds: float | None = None
    settings_file: str | None = None


def valid_timeout(value: object) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    return math.isfinite(value) and TIMEOUT_RANGE[0] <= value <= TIMEOUT_RANGE[1]


def parse_arguments(args: list[str]) -> Command:
    name: str | None = None
    values: dict[str, str] = {}
    index = 0
    while index < len(args):
        arg = args[index]
        index += 1
        if arg.startswith("--"):
            key, equals, value = arg[2:].partition("=")
            if key not in ("timeout", "settings"):
                raise Failure("invalid_input", "Unknown option. The options are --timeout <seconds> and --settings <file>.")
            if key in values:
                raise Failure("invalid_input", f"Option --{key} may be given once.")
            if not equals:
                value = args[index] if index < len(args) else ""
                index += 1
                if value.startswith("--"):
                    value = ""
            if not value:
                raise Failure("invalid_input", f"Option --{key} needs a value.")
            values[key] = value
        elif arg.startswith("-"):
            raise Failure(
                "invalid_input", "Unknown option. A Build is chosen with -v as the first argument of the launcher."
            )
        elif name is None:
            name = arg
        else:
            raise Failure("invalid_input", "A command takes no further arguments.")
    if name is None:
        raise Failure("invalid_input", "Name a command: classify, info or add-key.")
    if name not in COMMANDS:
        raise Failure("invalid_input", "Unknown command. The commands are classify, info and add-key.")
    for key in values:
        if key not in COMMANDS[name]:
            raise Failure("invalid_input", f"Option --{key} does not apply to {name}.")
    timeout: float | None = None
    if "timeout" in values:
        text = values["timeout"]
        timeout = float(text) if NUMBER.fullmatch(text) else None
        if not valid_timeout(timeout):
            raise Failure("invalid_input", "--timeout takes a number of seconds from 1 to 60.")
    return Command(name, timeout, values.get("settings"))
