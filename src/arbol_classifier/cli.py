"""One invocation, one command: one JSON document on standard output, status 0 or 1."""

import os
import select
import sys
import time
from collections.abc import Callable, Mapping
from pathlib import Path

from . import CONTRACT, NAME
from .arguments import parse_arguments
from .build import build_identity
from .classify import classify
from .errors import Failure
from .json_types import Object, dumps
from .key import ACCOUNT, SERVICE, can_be_key, key_found, store_key
from .limits import Deadline
from .settings import read_settings, settings_path
from .terminal import NOTHING_STORED, ask_for_key


def standard_input(deadline: Deadline) -> bytes:
    """The request on standard input, read until it ends or the time limit of the call is reached."""
    chunks: list[bytes] = []
    try:
        fd = sys.stdin.fileno()
        while True:
            remaining = deadline.remaining()
            if remaining <= 0:
                raise deadline.reached("while the request was read on standard input")
            if not select.select([fd], [], [], remaining)[0]:
                continue
            chunk = os.read(fd, 65536)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)
    except (OSError, AttributeError, ValueError):
        raise Failure("invalid_input", "Cannot read the request on standard input.") from None


def add_key(ask: Callable[[], str]) -> Object:
    """Ask for the key at the terminal and store it in the Keychain item (CLS-0.16)."""
    key = ask().strip()
    if not key:
        raise Failure("invalid_input", f"No key was typed. {NOTHING_STORED}")
    if not can_be_key(key):
        raise Failure(
            "invalid_input",
            "What was typed cannot be a Jev API key, which is one line of visible characters without spaces. "
            + NOTHING_STORED,
        )
    replaced = store_key(key)
    return {"keychain": {"service": SERVICE, "account": ACCOUNT}, "replaced": replaced}


def run(
    args: list[str],
    environ: Mapping[str, str],
    read_input: Callable[[Deadline], bytes] = standard_input,
    ask: Callable[[], str] = ask_for_key,
) -> tuple[int, Object]:
    started = time.monotonic()
    try:
        command = parse_arguments(args)
        if command.name == "add-key":
            return 0, add_key(ask)
        home = environ.get("HOME") or str(Path.home())
        file = Path(os.path.abspath(command.settings_file)) if command.settings_file else settings_path(home)
        settings = read_settings(file)
        if command.name == "info":
            version, build = build_identity()
            return 0, {
                "name": NAME,
                "version": version,
                "build": build,
                "contract": CONTRACT,
                "settingsFile": str(file),
                "model": settings.model,
                "endpoint": settings.endpoint,
                "keyFound": key_found(settings, file, settings.timeout_seconds),
            }
        timeout = command.timeout_seconds if command.timeout_seconds is not None else settings.timeout_seconds
        deadline = Deadline(timeout, started)
        return 0, classify(read_input(deadline), settings, file, deadline)
    except Failure as failure:
        return 1, {"error": failure.error()}
    except Exception as error:
        print(f"{NAME}: unexpected {type(error).__name__}", file=sys.stderr)
        return 1, {"error": Failure("internal", f"{NAME} could not complete the command.").error()}


def entry() -> None:
    status, document = run(sys.argv[1:], os.environ)
    sys.stdout.buffer.write((dumps(document) + "\n").encode("utf-8"))
    sys.stdout.flush()
    sys.exit(status)
