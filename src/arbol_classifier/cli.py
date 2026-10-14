"""One invocation, one command: one JSON document on standard output, status 0 or 1."""

import os
import sys
from collections.abc import Callable, Mapping
from pathlib import Path

from . import CONTRACT, NAME
from .arguments import parse_arguments
from .build import build_identity
from .classify import classify
from .errors import Failure
from .json_types import Object, dumps
from .settings import read_settings, settings_path


def standard_input() -> bytes:
    try:
        return sys.stdin.buffer.read()
    except (OSError, AttributeError, ValueError):
        raise Failure("invalid_input", "Cannot read the request on standard input.") from None


def run(
    args: list[str], environ: Mapping[str, str], read_input: Callable[[], bytes] = standard_input
) -> tuple[int, Object]:
    try:
        command = parse_arguments(args)
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
                "keyFound": False,  # The key is looked for from SYL-161 on.
            }
        timeout = command.timeout_seconds if command.timeout_seconds is not None else settings.timeout_seconds
        return 0, classify(read_input(), settings, file, timeout)
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
