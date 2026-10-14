"""The contract check of CLS-0: start the built program as a program and read what it prints.

Each scenario runs the Build's own program with a fresh home folder and checks its
standard output, its standard error and its exit status. From SYL-152 on it covers
`info`, the settings file and the refusals of the command line (CLS-0.14).
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

NAME = "arbol-classifier"
CODES = ("invalid_input", "not_signed_in", "credential_rejected", "rate_limited", "vendor_unavailable",
         "vendor_error", "limit_reached", "internal")
DEFAULT_MODEL = "jev-1.13.0"
DEFAULT_ENDPOINT = "https://api.typesafe.ai/v1/systemone"
INFO_FIELDS = {"name", "version", "build", "contract", "settingsFile", "model", "endpoint", "keyFound"}


class ContractFailure(Exception):
    pass


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise ContractFailure(message)


@dataclass(frozen=True)
class Outcome:
    status: int
    stdout: str
    stderr: str
    document: dict[str, Any]


@dataclass
class Contract:
    program: Path
    build_folder: Path
    version: str
    build: str
    home: Path

    def call(self, *args: str, cwd: Path | None = None) -> Outcome:
        result = subprocess.run([str(self.program), *args], cwd=cwd or self.home, stdin=subprocess.DEVNULL,
                                env={"HOME": str(self.home), "PATH": "/usr/bin:/bin", "LANG": "C"},
                                capture_output=True, timeout=60, check=False)
        stdout = result.stdout.decode("utf-8")
        stderr = result.stderr.decode("utf-8", "replace")
        expect(result.returncode in (0, 1), f"exit status {result.returncode} for {list(args)}")
        expect(stdout.endswith("\n") and stdout.count("\n") == 1,
               f"standard output is not one line for {list(args)}")
        try:
            document = json.loads(stdout)
        except ValueError:
            raise ContractFailure(f"standard output is not one JSON document for {list(args)}") from None
        expect(isinstance(document, dict), f"standard output is not a JSON object for {list(args)}")
        return Outcome(result.returncode, stdout, stderr, document)

    def info(self, *args: str, cwd: Path | None = None) -> dict[str, Any]:
        outcome = self.call("info", *args, cwd=cwd)
        expect(outcome.status == 0, f"info {list(args)} ended with status {outcome.status}: {outcome.stdout}")
        expect(outcome.stderr == "", f"info {list(args)} wrote to standard error: {outcome.stderr}")
        expect(set(outcome.document) == INFO_FIELDS, f"info fields are {sorted(outcome.document)}")
        return outcome.document

    def refused(self, *args: str, names: tuple[str, ...] = (), hidden: tuple[str, ...] = ()) -> dict[str, Any]:
        outcome = self.call(*args)
        expect(outcome.status == 1, f"{list(args)} ended with status {outcome.status}, not 1")
        expect(set(outcome.document) == {"error"}, f"{list(args)} printed more than an error: {outcome.stdout}")
        error: dict[str, Any] = outcome.document["error"]
        expect(isinstance(error, dict), f"{list(args)} printed an error that is not an object")
        expect(error.get("code") == "invalid_input", f"{list(args)} was refused with {error.get('code')}")
        expect(error.get("code") in CODES and error.get("retryable") is False,
               f"{list(args)} printed an error object outside CLS-0: {error}")
        expect(isinstance(error.get("message"), str) and bool(error["message"]), f"{list(args)} has no message")
        for name in names:
            expect(name in error["message"], f"the message for {list(args)} does not name {name}: {error['message']}")
        for value in hidden:
            expect(value not in outcome.stdout and value not in outcome.stderr,
                   f"the output for {list(args)} shows the value {value!r}")
        expect(outcome.stderr == "", f"{list(args)} wrote to standard error: {outcome.stderr}")
        return error

    def settings(self, value: object, name: str = ".arbol/arbol-classifier.json") -> Path:
        file = self.home / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(value if isinstance(value, str) else json.dumps(value), encoding="utf-8")
        return file


SCENARIOS: list[tuple[str, Callable[[Contract], None]]] = []


def scenario(name: str) -> Callable[[Callable[[Contract], None]], Callable[[Contract], None]]:
    def register(function: Callable[[Contract], None]) -> Callable[[Contract], None]:
        SCENARIOS.append((name, function))
        return function

    return register


@scenario("info.identity")
def info_identity(contract: Contract) -> None:
    info = contract.info()
    expect(info["name"] == NAME, f"name is {info['name']!r}")
    expect(info["version"] == contract.version, f"version is {info['version']!r}, not {contract.version!r}")
    expect(info["build"] == contract.build, f"build is {info['build']!r}, not {contract.build!r}")
    expect(info["contract"] == 1 and type(info["contract"]) is int, f"contract is {info['contract']!r}")
    expect(info["keyFound"] is False, f"keyFound is {info['keyFound']!r}")


@scenario("info.defaults")
def info_defaults(contract: Contract) -> None:
    info = contract.info()
    expect(info["settingsFile"] == str(contract.home / ".arbol/arbol-classifier.json"),
           f"settingsFile is {info['settingsFile']!r}")
    expect(info["model"] == DEFAULT_MODEL, f"model is {info['model']!r}")
    expect(info["endpoint"] == DEFAULT_ENDPOINT, f"endpoint is {info['endpoint']!r}")


@scenario("info.settings-file")
def info_settings_file(contract: Contract) -> None:
    file = contract.settings({"model": "jev-1.14.0", "timeoutSeconds": 5, "maxRequestBytes": 32000,
                              "endpoint": "http://127.0.0.1:8649/v1/systemone", "secret": {"from": "keychain"}})
    info = contract.info()
    expect(info["settingsFile"] == str(file), f"settingsFile is {info['settingsFile']!r}")
    expect(info["model"] == "jev-1.14.0", f"model is {info['model']!r}")
    expect(info["endpoint"] == "http://127.0.0.1:8649/v1/systemone", f"endpoint is {info['endpoint']!r}")


@scenario("info.settings-option")
def info_settings_option(contract: Contract) -> None:
    contract.settings({"model": "jev-1.14.0"})
    other = contract.settings({"model": "jev-2.0.0", "endpoint": "http://localhost:9/v1/systemone"}, "tests/other.json")
    for args in (("--settings", "tests/other.json"), (f"--settings={other}",)):
        info = contract.info(*args, cwd=contract.home)
        expect(info["settingsFile"] == str(other), f"settingsFile is {info['settingsFile']!r} for {list(args)}")
        expect(info["model"] == "jev-2.0.0" and info["endpoint"] == "http://localhost:9/v1/systemone",
               f"info did not read {other} for {list(args)}")
    missing = contract.home / "tests/missing.json"
    info = contract.info("--settings", str(missing))
    expect(info["settingsFile"] == str(missing) and info["model"] == DEFAULT_MODEL,
           "a missing settings file named with --settings did not give the defaults")


@scenario("info.accepted-settings")
def info_accepted_settings(contract: Contract) -> None:
    for value in (
        {},
        {"model": "jev-2.10.3", "timeoutSeconds": 2.5, "maxRequestBytes": 1, "endpoint": "http://[::1]:7000/v1/systemone",
         "secret": {"from": "command", "command": ["/usr/bin/true"]}},
        {"timeoutSeconds": 1, "endpoint": "https://localhost/v1/systemone"},
        {"timeoutSeconds": 60, "endpoint": DEFAULT_ENDPOINT, "secret": {"from": "keychain"}},
    ):
        contract.settings(value)
        info = contract.info()
        expect(info["model"] == value.get("model", DEFAULT_MODEL), f"model is {info['model']!r} for {value}")
        expect(info["endpoint"] == value.get("endpoint", DEFAULT_ENDPOINT), f"endpoint is {info['endpoint']!r}")


@scenario("settings.faulty-file")
def settings_faulty_file(contract: Contract) -> None:
    file = contract.home / ".arbol/arbol-classifier.json"
    for text in ("{", "[]", '"jev-1.13.0"', "null", '{"timeoutSeconds": NaN}', ""):
        contract.settings(text)
        contract.refused("info", names=(str(file),))
    file.unlink()
    file.mkdir()
    contract.refused("info", names=(str(file),))


@scenario("settings.unknown-key")
def settings_unknown_key(contract: Contract) -> None:
    file = contract.settings({"timoutSeconds": 5})
    contract.refused("info", names=(str(file), "timoutSeconds"))
    contract.settings({"secret": {"from": "keychain", "account": "jev"}})
    contract.refused("info", names=("secret.account",))
    contract.settings({"secret": {"from": "command", "command": ["/usr/bin/true"], "env": {}}})
    contract.refused("info", names=("secret.env",))


@scenario("settings.moving-model")
def settings_moving_model(contract: Contract) -> None:
    for model in ("jev-latest", "jev-preview", "jev-1.13", "jev-1.13.0-preview", "Jev-1.13.0", "jev-01.13.0"):
        contract.settings({"model": model})
        contract.refused("info", names=("model",), hidden=(model,))


@scenario("settings.faulty-fields")
def settings_faulty_fields(contract: Contract) -> None:
    cases: list[tuple[object, str, tuple[str, ...]]] = [
        ({"model": 5}, "model", ()),
        ({"model": ""}, "model", ()),
        ({"timeoutSeconds": "10"}, "timeoutSeconds", ()),
        ({"timeoutSeconds": 0}, "timeoutSeconds", ()),
        ({"timeoutSeconds": 0.5}, "timeoutSeconds", ()),
        ({"timeoutSeconds": 61}, "timeoutSeconds", ()),
        ({"timeoutSeconds": True}, "timeoutSeconds", ()),
        ('{"timeoutSeconds": 1e400}', "timeoutSeconds", ()),
        ({"maxRequestBytes": 0}, "maxRequestBytes", ()),
        ({"maxRequestBytes": 1.5}, "maxRequestBytes", ()),
        ({"maxRequestBytes": "64000"}, "maxRequestBytes", ()),
        ({"maxRequestBytes": False}, "maxRequestBytes", ()),
        ({"endpoint": "https://example.com/v1/systemone"}, "endpoint", ("example.com",)),
        ({"endpoint": "https://api.typesafe.ai/v2/systemone"}, "endpoint", ("v2/systemone",)),
        ({"endpoint": "http://192.168.1.20:8080/v1/systemone"}, "endpoint", ("192.168.1.20",)),
        ({"endpoint": "http://127.0.0.1.example.net/v1"}, "endpoint", ("example.net",)),
        ({"endpoint": "http://localhost@example.org/v1"}, "endpoint", ("example.org",)),
        ({"endpoint": "ftp://localhost/v1"}, "endpoint", ("ftp:",)),
        ({"endpoint": "localhost:8080"}, "endpoint", ("localhost:8080",)),
        ({"endpoint": ["http://localhost/"]}, "endpoint", ()),
        ({"secret": "keychain"}, "secret", ()),
        ({"secret": {}}, "secret.from", ()),
        ({"secret": {"from": "plain-file-marker"}}, "secret.from", ("plain-file-marker",)),
        ({"secret": {"from": "command"}}, "secret.command", ()),
        ({"secret": {"from": "command", "command": []}}, "secret.command", ()),
        ({"secret": {"from": "command", "command": ["", "print-key"]}}, "secret.command", ("print-key",)),
        ({"secret": {"from": "command", "command": "print-key-marker"}}, "secret.command", ("print-key-marker",)),
    ]
    for value, name, hidden in cases:
        file = contract.settings(value)
        contract.refused("info", names=(str(file), name), hidden=hidden)


@scenario("cli.no-command")
def cli_no_command(contract: Contract) -> None:
    contract.refused()
    contract.refused("--settings", "tests/other.json")


@scenario("cli.unknown-command")
def cli_unknown_command(contract: Contract) -> None:
    for command in ("judge-this-marker", "Info", "help"):
        contract.refused(command, hidden=(command,) if command != "help" else ())


@scenario("cli.unknown-option")
def cli_unknown_option(contract: Contract) -> None:
    for args in (("info", "--verbose"), ("info", "--state-dir", "/tmp/state"), ("info", "-h"), ("info", "--"),
                 ("--key=secret-marker", "info")):
        contract.refused(*args, hidden=("secret-marker",))


@scenario("cli.build-selector")
def cli_build_selector(contract: Contract) -> None:
    contract.refused("-v", "3", "info")
    contract.refused("info", "-v", "3")


@scenario("cli.extra-argument")
def cli_extra_argument(contract: Contract) -> None:
    contract.refused("info", "now")
    contract.refused("info", "classify")


@scenario("cli.option-once")
def cli_option_once(contract: Contract) -> None:
    contract.refused("info", "--settings", "a.json", "--settings", "b.json", names=("--settings",))
    contract.refused("classify", "--timeout", "5", "--timeout=6", names=("--timeout",))


@scenario("cli.option-value")
def cli_option_value(contract: Contract) -> None:
    contract.refused("info", "--settings", names=("--settings",))
    contract.refused("info", "--settings=", names=("--settings",))
    contract.refused("info", "--settings", "--settings", names=("--settings",))
    contract.refused("classify", "--timeout", names=("--timeout",))


@scenario("cli.timeout")
def cli_timeout(contract: Contract) -> None:
    contract.refused("info", "--timeout", "5", names=("--timeout",))
    for value in ("0", "0.5", "61", "60.5", "ten", "-5", "1e1", " 5", "５"):
        contract.refused("classify", "--timeout", value, names=("--timeout",))
        contract.refused("classify", f"--timeout={value}", names=("--timeout",))


def snapshot(*roots: Path) -> dict[str, tuple[int, int]]:
    """Every file and folder under the roots, except the Build's record and log, which the build tool writes."""
    found: dict[str, tuple[int, int]] = {}
    for root in roots:
        for directory, folders, files in os.walk(root):
            for name in [*folders, *files]:
                path = Path(directory, name)
                if path.parent == root and name in ("build.json", "build.log"):
                    continue
                status = path.lstat()
                found[str(path)] = (status.st_mtime_ns, status.st_size)
    return found


def run_contract(program: Path, build_folder: Path, version: str, build: str) -> int:
    failed = 0
    with tempfile.TemporaryDirectory(prefix="arbol-classifier-contract-") as name:
        base = Path(name).resolve()
        before = snapshot(build_folder)
        for index, (title, function) in enumerate(SCENARIOS):
            home = base / f"home-{index}"
            home.mkdir()
            contract = Contract(program, build_folder, version, build, home)
            try:
                function(contract)
            except (ContractFailure, OSError, subprocess.TimeoutExpired, UnicodeDecodeError) as error:
                failed += 1
                print(f"FAILED {title}: {error}", flush=True)
            else:
                print(f"passed {title}", flush=True)
        title = "info.writes-nothing"
        home = base / "home-quiet"
        (home / ".arbol").mkdir(parents=True)
        (home / ".arbol/arbol-classifier.json").write_text('{"model": "jev-1.14.0"}')
        contract = Contract(program, build_folder, version, build, home)
        quiet_before = snapshot(home)
        try:
            contract.info()
            contract.refused("info", "--timeout", "5")
            expect(snapshot(home) == quiet_before, "a call changed the home folder")
            expect(snapshot(build_folder) == before, "the calls changed the Build's folder")
        except (ContractFailure, OSError, subprocess.TimeoutExpired, UnicodeDecodeError) as error:
            failed += 1
            print(f"FAILED {title}: {error}", flush=True)
        else:
            print(f"passed {title}", flush=True)
    total = len(SCENARIOS) + 1
    print(json.dumps({"check": "contract", "scenarios": total, "passed": total - failed, "failed": failed}), flush=True)
    return 1 if failed else 0
