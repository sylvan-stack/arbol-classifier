"""A stand-in for the system's `security` command, for the unit and the contract checks (CLS-0, "The key").

It keeps generic passwords in a folder of its own instead of the Keychain, and records every
time it is started: its arguments, what it read on standard input and its environment. It
knows the commands the classifier uses, in the forms the real command takes them:
`find-generic-password` with or without `-w`, `add-generic-password` and
`delete-generic-password`, given as arguments or as lines on standard input after `-i`. An item
that does not exist ends with status 44, as with the real command.

    python -I -B security_stand_in.py <folder> <arguments of security>

`SecurityStandIn` prepares such a folder and an executable `security` in it that starts this
script, so that the path of that file can take the place of `/usr/bin/security`.
"""

from __future__ import annotations

import json
import os
import shlex
import sys
from pathlib import Path
from typing import Any

NOT_FOUND = 44
DUPLICATE = 45


def words(line: str) -> list[str]:
    """A line of `security -i`, split as the real command splits it: double quotes group, a backslash escapes."""
    result: list[str] = []
    current: list[str] = []
    started = quoted = escaped = False
    for character in line:
        if escaped:
            current.append(character)
            escaped = False
        elif character == "\\":
            escaped = started = True
        elif character == '"':
            quoted = not quoted
            started = True
        elif character.isspace() and not quoted:
            if started:
                result.append("".join(current))
            current, started = [], False
        else:
            current.append(character)
            started = True
    if quoted or escaped:
        raise ValueError("unbalanced quoting")
    if started:
        result.append("".join(current))
    return result


class Store:
    def __init__(self, folder: Path) -> None:
        self.folder = folder
        self.items_file = folder / "items.json"

    def items(self) -> dict[str, str]:
        if not self.items_file.exists():
            return {}
        value: dict[str, str] = json.loads(self.items_file.read_text(encoding="utf-8"))
        return value

    def write(self, items: dict[str, str]) -> None:
        self.items_file.write_text(json.dumps(items), encoding="utf-8")


def item_name(service: str, account: str) -> str:
    return f"{service}\t{account}"


def options(args: list[str], flags: str) -> tuple[dict[str, str], set[str]]:
    """The options of one command: `-s value` and the like, and the flags without a value such as `-w` at the end."""
    values: dict[str, str] = {}
    seen: set[str] = set()
    index = 0
    while index < len(args):
        option = args[index]
        index += 1
        if not option.startswith("-") or len(option) != 2:
            raise ValueError(f"unexpected argument {option!r}")
        if option[1] in flags:
            seen.add(option)
        elif option == "-w" and index == len(args):
            seen.add(option)  # -w as the last option: the real command would ask at the terminal
        elif index < len(args):
            values[option] = args[index]
            index += 1
        else:
            raise ValueError(f"option {option} needs a value")
    return values, seen


def command(store: Store, args: list[str], out: list[str], err: list[str]) -> int:
    if not args:
        err.append("usage: security command")
        return 2
    name, rest = args[0], args[1:]
    items = store.items()
    if name == "find-generic-password":
        values, flags = options(rest, "wg")
        key = item_name(values.get("-s", ""), values.get("-a", ""))
        if key not in items:
            err.append("security: SecKeychainSearchCopyNext: The specified item could not be found in the keychain.")
            return NOT_FOUND
        if "-w" in flags:
            out.append(items[key] + "\n")
        else:
            out.append(f'keychain: "{store.folder}/login.keychain-db"\nclass: "genp"\nattributes:\n'
                       f'    "acct"<blob>="{values.get("-a", "")}"\n    "svce"<blob>="{values.get("-s", "")}"\n')
        return 0
    if name == "add-generic-password":
        values, flags = options(rest, "UA")
        if "-w" not in values:
            err.append("security: the stand-in does not ask at a terminal")
            return 1
        key = item_name(values.get("-s", ""), values.get("-a", ""))
        if key in items and "-U" not in flags:
            err.append("security: SecKeychainItemCreateFromContent: The specified item already exists in the keychain.")
            return DUPLICATE
        items[key] = values["-w"]
        store.write(items)
        return 0
    if name == "delete-generic-password":
        values, _ = options(rest, "")
        key = item_name(values.get("-s", ""), values.get("-a", ""))
        if key not in items:
            err.append("security: SecKeychainSearchCopyNext: The specified item could not be found in the keychain.")
            return NOT_FOUND
        del items[key]
        store.write(items)
        return 0
    err.append(f"security: unknown command {name}")
    return 2


def main(arguments: list[str]) -> int:
    folder = Path(arguments[0])
    args = arguments[1:]
    store = Store(folder)
    data = sys.stdin.read() if args == ["-i"] else ""
    with (folder / "calls.jsonl").open("a", encoding="utf-8") as log:
        log.write(json.dumps({"args": args, "stdin": data, "env": dict(os.environ)}) + "\n")
    failure = folder / "fail.json"
    if failure.exists():
        status = int(json.loads(failure.read_text(encoding="utf-8"))["status"])
        print(f"security: the stand-in fails with status {status}", file=sys.stderr)
        return status
    out: list[str] = []
    err: list[str] = []
    try:
        if args == ["-i"]:
            status = 0
            for line in data.splitlines():
                if line.strip():
                    status = command(store, words(line), out, err)
                    if status:
                        break
        else:
            status = command(store, args, out, err)
    except ValueError as error:
        err.append(f"security: {error}")
        status = 2
    sys.stdout.write("".join(out))
    if err:
        print("\n".join(err), file=sys.stderr)
    return status


class SecurityStandIn:
    """A folder with an executable `security` that runs the stand-in, and what the stand-in holds and recorded."""

    def __init__(self, folder: Path, python: str | None = None) -> None:
        self.folder = folder
        folder.mkdir(parents=True, exist_ok=True)
        self.program = folder / "security"
        script = Path(__file__).resolve()
        self.program.write_text(
            "#!/bin/sh\nexec " + " ".join(shlex.quote(part) for part in
                                          (python or sys.executable, "-I", "-B", str(script), str(folder)))
            + ' "$@"\n', encoding="utf-8")
        self.program.chmod(0o755)
        self.store = Store(folder)

    def put(self, service: str, account: str, value: str) -> None:
        self.store.write({**self.store.items(), item_name(service, account): value})

    def value(self, service: str, account: str) -> str | None:
        return self.store.items().get(item_name(service, account))

    def fail(self, status: int | None) -> None:
        failure = self.folder / "fail.json"
        if status is None:
            failure.unlink(missing_ok=True)
        else:
            failure.write_text(json.dumps({"status": status}), encoding="utf-8")

    def calls(self) -> list[dict[str, Any]]:
        log = self.folder / "calls.jsonl"
        if not log.exists():
            return []
        return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
