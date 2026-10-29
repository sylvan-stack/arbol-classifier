# Test implementations moved to tests/mid/archived/scripts/contract_checks.py.
"""The contract check of CLS-0: start the built program as a program and read what it prints.

Each scenario runs the Build's own program with a fresh home folder and checks its
standard output, its standard error and its exit status. From SYL-152 on it covers
`info`, the settings file and the refusals of the command line (CLS-0.14). From SYL-157
on it covers `classify` against the stand-in for Jev, which records what it was sent.
From SYL-161 on it covers the key: from the Keychain item or the key command, and
`add-key` at a pretend terminal. From SYL-162 on it covers the table of errors, the
attempts, the waits and the time limit; a call about time runs with its times shortened.

The program is started through `scripts/contract_entry.py`, which puts the stand-in for
`security` in the place of `/usr/bin/security`, so that no scenario reaches the real
Keychain. One scenario, `cli.build-entry`, starts the Build's entry `bin/arbol-classifier`
itself, with a key command in its settings.
"""

from __future__ import annotations

import json
import os
import select
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jev_stand_in import Received, Reply, StandIn, like_jev
from security_stand_in import SecurityStandIn

NAME = "arbol-classifier"
CODES = ("invalid_input", "not_signed_in", "credential_rejected", "rate_limited", "vendor_unavailable",
         "vendor_error", "limit_reached", "internal")
DEFAULT_MODEL = "jev-1.13.0"
DEFAULT_ENDPOINT = "https://api.typesafe.ai/v1/systemone"
INFO_FIELDS = {"name", "version", "build", "contract", "settingsFile", "model", "endpoint", "keyFound"}
KEY = "contract-check-key-5c1e"  # given by the key command of the test settings; not a Jev key
KEY_SECOND = "contract-check-key-second-7a2d"
TYPED = "contract-check-typed-key-91b0"  # typed at the pretend terminal in add-key
TYPED_SECOND = 'contract-check-typed-key-second-"3f6e\\'  # with a quote and a backslash
TEST_KEYS = (KEY, KEY_SECOND, TYPED, TYPED_SECOND)
JUDGED = "Judged text marker: can you also update the README while you are at it?"
SERVICE = "com.sylvan-stack.arbol.classifier"
ACCOUNT = "jev"
NO_KEY = ("No Jev API key was found. arbol-classifier looked in the login Keychain for the item with the service "
          f"{SERVICE} and the account {ACCOUNT}")
STORE = "arbol-classifier add-key"
FIND = ["find-generic-password", "-s", SERVICE, "-a", ACCOUNT, "-w"]
# It makes the pretend terminal on its standard input its controlling terminal, in a session of its own, and then
# starts the program, which finds the pretend terminal as /dev/tty.
AT_TERMINAL = ("import fcntl, os, sys, termios\nos.setsid()\nfcntl.ioctl(0, termios.TIOCSCTTY, 0)\n"
               "os.execv(sys.argv[1], sys.argv[1:])\n")


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
    seconds: float = 0.0  # how long the call took, measured by the check


@dataclass
class Contract:
    program: Path
    build_folder: Path
    version: str
    build: str
    home: Path
    work: Path  # beside the home folder: the test settings for classify and the file the key command prints
    security: SecurityStandIn  # in the place of /usr/bin/security, in the work folder

    @property
    def python(self) -> Path:
        return self.build_folder / "runtime/python/bin/python3.14"

    def command(self, *args: str, entry: bool = False, scale: float = 1.0) -> list[str]:
        """The Build's own entry, or the same program with the stand-in for security and every time of a call
        multiplied by `scale` (contract_entry.py)."""
        if entry:
            return [str(self.program), *args]
        return [str(self.python), "-I", "-B", str(self.build_folder / "scripts/contract_entry.py"),
                str(self.security.program), repr(scale), *args]

    def environment(self, env: dict[str, str] | None = None) -> dict[str, str]:
        return {"HOME": str(self.home), "PATH": "/usr/bin:/bin", "LANG": "C", **(env or {})}

    def call(self, *args: str, cwd: Path | None = None, data: bytes | None = None,
             env: dict[str, str] | None = None, entry: bool = False, scale: float = 1.0) -> Outcome:
        """One call without a terminal: in a session of its own, so that it cannot reach the terminal of the check."""
        started = time.monotonic()
        result = subprocess.run(self.command(*args, entry=entry, scale=scale), cwd=cwd or self.home,
                                input=data or b"", env=self.environment(env), capture_output=True, timeout=60,
                                check=False, start_new_session=True)
        return self.outcome(list(args), result.returncode, result.stdout, result.stderr, time.monotonic() - started)

    def at_terminal(self, *args: str, typed: bytes) -> tuple[Outcome, bytes]:
        """One call at a pretend terminal: type `typed` when the program asks, and give what the terminal showed."""
        master, slave = os.openpty()
        try:
            process = subprocess.Popen([str(self.python), "-I", "-B", "-c", AT_TERMINAL, *self.command(*args)],
                                       stdin=slave, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.home,
                                       env=self.environment())
        finally:
            os.close(slave)
        shown = b""
        try:
            end = time.monotonic() + 30
            while not (b"Jev API key" in shown and shown.endswith(b": ")) and time.monotonic() < end:
                ready, _, _ = select.select([master], [], [], 0.1)
                if ready:
                    try:
                        chunk = os.read(master, 1024)
                    except OSError:
                        break
                    if not chunk:
                        break
                    shown += chunk
                elif process.poll() is not None:
                    break
            if process.poll() is None:
                os.write(master, typed)
            # The terminal is read until the program has ended: macOS lets a program that holds a terminal end
            # only when what it wrote there has been read.
            end = time.monotonic() + 60
            while time.monotonic() < end:
                if select.select([master], [], [], 0.1)[0]:
                    try:
                        chunk = os.read(master, 1024)
                    except OSError:
                        chunk = b""
                    shown += chunk
                    if chunk:
                        continue
                if process.poll() is not None:
                    break
            stdout, stderr = process.communicate(timeout=5)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            os.close(master)
        outcome = self.outcome(list(args), process.returncode, stdout, stderr)
        expect_no_key(shown.decode("utf-8", "replace"), f"the terminal of {list(args)}")
        return outcome, shown

    def outcome(self, args: list[str], status: int, out: bytes, err: bytes, seconds: float = 0.0) -> Outcome:
        stdout = out.decode("utf-8")
        stderr = err.decode("utf-8", "replace")
        expect_no_key(stdout + stderr, f"the output of {args}")
        expect(status in (0, 1), f"exit status {status} for {args}")
        expect(stdout.endswith("\n") and stdout.count("\n") == 1, f"standard output is not one line for {args}")
        try:
            document = json.loads(stdout)
        except ValueError:
            raise ContractFailure(f"standard output is not one JSON document for {args}") from None
        expect(isinstance(document, dict), f"standard output is not a JSON object for {args}")
        return Outcome(status, stdout, stderr, document, seconds)

    def keychain_settings(self, stand_in: StandIn, name: str = "keychain.json", **fields: object) -> Path:
        """Test settings with the stand-in for Jev as endpoint, and no key command: the key comes from the item."""
        file = self.work / name
        file.write_text(json.dumps({"endpoint": stand_in.url, **fields}), encoding="utf-8")
        return file

    def info(self, *args: str, cwd: Path | None = None) -> dict[str, Any]:
        outcome = self.call("info", *args, cwd=cwd)
        expect(outcome.status == 0, f"info {list(args)} ended with status {outcome.status}: {outcome.stdout}")
        expect(outcome.stderr == "", f"info {list(args)} wrote to standard error: {outcome.stderr}")
        expect(set(outcome.document) == INFO_FIELDS, f"info fields are {sorted(outcome.document)}")
        return outcome.document

    def refused(self, *args: str, names: tuple[str, ...] = (), hidden: tuple[str, ...] = ()) -> dict[str, Any]:
        return failed(self.call(*args), list(args), "invalid_input", names, hidden)

    def settings(self, value: object, name: str = ".arbol/arbol-classifier.json") -> Path:
        file = self.home / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(value if isinstance(value, str) else json.dumps(value), encoding="utf-8")
        return file

    def classify_settings(self, stand_in: StandIn, **fields: object) -> Path:
        """Test settings beside the home folder: the stand-in as endpoint, and a command that prints KEY."""
        key_file = self.work / "key.txt"
        key_file.write_text(KEY + "\n", encoding="utf-8")
        value = {"endpoint": stand_in.url, "secret": {"from": "command", "command": ["/bin/cat", str(key_file)]},
                 **fields}
        file = self.work / "settings.json"
        file.write_text(json.dumps(value), encoding="utf-8")
        return file

    def classify(self, request: object, settings: Path, *args: str, env: dict[str, str] | None = None,
                 scale: float = 1.0) -> Outcome:
        """One classify call. Neither the judged text nor the key may appear in what it prints."""
        data = request if isinstance(request, bytes) else json.dumps(request).encode("utf-8")
        outcome = self.call("classify", "--settings", str(settings), *args, data=data, env=env, scale=scale)
        expect(JUDGED not in outcome.stdout and JUDGED not in outcome.stderr, "classify printed the judged text")
        expect(outcome.stderr == "", f"classify wrote to standard error: {outcome.stderr}")
        return outcome

    def answered(self, request: object, settings: Path, stand_in: StandIn, *args: str) -> dict[str, Any]:
        """A classify call that succeeds: one request sent, and the reply printed as the stand-in gave it."""
        sent = len(stand_in.received)
        outcome = self.classify(request, settings, *args)
        expect(outcome.status == 0, f"classify ended with status {outcome.status}: {outcome.stdout}")
        expect(len(stand_in.received) == sent + 1, f"classify sent {len(stand_in.received) - sent} requests, not 1")
        expect(outcome.document == json.loads(stand_in.replies[-1].body),
               f"classify did not print the reply as Jev gave it: {outcome.stdout}")
        return outcome.document

    def classify_failed(self, request: object, settings: Path, stand_in: StandIn, code: str,
                        names: tuple[str, ...] = (), sends: int = 0, args: tuple[str, ...] = (),
                        scale: float = 1.0) -> dict[str, Any]:
        sent = len(stand_in.received)
        error = failed(self.classify(request, settings, *args, scale=scale), ["classify"], code, names, ())
        expect(len(stand_in.received) == sent + sends,
               f"classify sent {len(stand_in.received) - sent} requests before it ended with {code}, not {sends}")
        return error


def forms(value: str) -> set[str]:
    """A value as it is, and as it is written inside a JSON text."""
    return {value, json.dumps(value)[1:-1]}


def expect_no_key(text: str, where: str) -> None:
    """None of the test keys, in any of its forms, is in the text."""
    for key in TEST_KEYS:
        for form in forms(key):
            expect(form not in text, f"{where} shows a test key")


def failed(outcome: Outcome, args: list[str], code: str, names: tuple[str, ...], hidden: tuple[str, ...]
           ) -> dict[str, Any]:
    """The call ended with status 1 and printed only the error object of DRV-4 with this code."""
    expect(outcome.status == 1, f"{args} ended with status {outcome.status}, not 1")
    expect(set(outcome.document) == {"error"}, f"{args} printed more than an error: {outcome.stdout}")
    error: dict[str, Any] = outcome.document["error"]
    expect(isinstance(error, dict), f"{args} printed an error that is not an object")
    expect(error.get("code") == code, f"{args} ended with {error.get('code')}, not {code}")
    expect(error.get("code") in CODES and error.get("retryable") is (code in ("rate_limited", "vendor_unavailable")),
           f"{args} printed an error object outside CLS-0: {error}")
    expect(isinstance(error.get("message"), str) and bool(error["message"]), f"{args} has no message")
    for name in names:
        expect(name in error["message"], f"the message for {args} does not name {name}: {error['message']}")
    for value in hidden:
        expect(value not in outcome.stdout and value not in outcome.stderr, f"the output for {args} shows {value!r}")
    expect(outcome.stderr == "", f"{args} wrote to standard error: {outcome.stderr}")
    return error


SCENARIOS: list[tuple[str, Callable[[Contract], None]]] = []


def scenario(name: str) -> Callable[[Callable[[Contract], None]], Callable[[Contract], None]]:
    def register(function: Callable[[Contract], None]) -> Callable[[Contract], None]:
        SCENARIOS.append((name, function))
        return function

    return register


@scenario("info.identity")
def info_identity(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("info.defaults")
def info_defaults(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("info.settings-file")
def info_settings_file(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("info.settings-option")
def info_settings_option(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("info.accepted-settings")
def info_accepted_settings(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("settings.faulty-file")
def settings_faulty_file(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("settings.unknown-key")
def settings_unknown_key(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("settings.moving-model")
def settings_moving_model(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("settings.faulty-fields")
def settings_faulty_fields(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("cli.no-command")
def cli_no_command(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("cli.unknown-command")
def cli_unknown_command(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("cli.unknown-option")
def cli_unknown_option(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("cli.build-selector")
def cli_build_selector(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("cli.extra-argument")
def cli_extra_argument(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("cli.option-once")
def cli_option_once(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("cli.option-value")
def cli_option_value(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("cli.timeout")
def cli_timeout(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


def choice_request() -> dict[str, Any]:
    return {"state": JUDGED, "questions": {"kind": {"type": "choice", "instructions": "What is this message?",
            "criteria": {"request": "It asks for work to be done", "question": "It asks for information only",
                         "other": None}}}}


def expect_sent(stand_in: StandIn, request: dict[str, Any], model: str = DEFAULT_MODEL) -> Received:
    """The last request the stand-in received is the request with `model` added and nothing else."""
    received = stand_in.received[-1]
    expect((received.method, received.path) == ("POST", "/v1/systemone"),
           f"classify sent {received.method} {received.path}")
    expect(received.json() == {**request, "model": model},
           f"the body sent is not the request with model {model} added: {received.body!r}")
    return received


@scenario("classify.choice")
def classify_choice(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("classify.noul")
def classify_noul(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("classify.score")
def classify_score(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("classify.what-is-sent")
def classify_what_is_sent(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("classify.pinned-model")
def classify_pinned_model(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("classify.other-model")
def classify_other_model(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("classify.missing-answer")
def classify_missing_answer(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("classify.names-a-model")
def classify_names_a_model(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("classify.size-limit")
def classify_size_limit(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("classify.malformed")
def classify_malformed(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("classify.passes-questions-through")
def classify_passes_questions_through(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("classify.endpoint-elsewhere")
def classify_endpoint_elsewhere(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("classify.writes-nothing")
def classify_writes_nothing(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


def bearer(received: Received) -> str | None:
    return next((value for name, value in received.headers if name.lower() == "authorization"), None)


def security_args(contract: Contract) -> list[list[str]]:
    return [call["args"] for call in contract.security.calls()]


@scenario("key.keychain")
def key_keychain(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("key.not-found")
def key_not_found(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("key.only-in-the-bearer-token")
def key_only_in_the_bearer_token(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("add-key.at-a-terminal")
def add_key_at_a_terminal(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("add-key.no-terminal")
def add_key_no_terminal(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("add-key.not-a-key")
def add_key_not_a_key(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("add-key.keychain-refuses")
def add_key_keychain_refuses(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("cli.add-key-arguments")
def cli_add_key_arguments(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("cli.build-entry")
def cli_build_entry(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


# From SYL-162: the table of errors, the attempts, the waits and the time limit (CLS-0.9, 0.11, 0.12).
# A scenario about time runs with every time of the call multiplied by a scale, so none waits for seconds.
QUICK = 0.01  # the waits become 5 and 10 milliseconds


def answering(*replies: Reply | None) -> Callable[[Received], Reply]:
    """A script that gives the replies in turn, the last one again; None answers as Jev would."""
    count = [0]

    def script(received: Received) -> Reply:
        reply = replies[min(count[0], len(replies) - 1)]
        count[0] += 1
        return like_jev(received) if reply is None else reply

    return script


def vendor_status(error: dict[str, Any], status: int) -> None:
    expect(error.get("detail") == {"basis": "fields", "vendorStatus": status},
           f"the error does not name Jev's status {status}: {error}")


@scenario("errors.credential-rejected")
def errors_credential_rejected(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("errors.invalid-at-jev")
def errors_invalid_at_jev(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("errors.rate-limited")
def errors_rate_limited(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("errors.vendor-unavailable")
def errors_vendor_unavailable(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("errors.vendor-error")
def errors_vendor_error(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("attempts.until-an-answer")
def attempts_until_an_answer(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("attempts.waits")
def attempts_waits(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("limits.no-wait-past-the-limit")
def limits_no_wait_past_the_limit(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


@scenario("limits.time-limit")
def limits_time_limit(contract: Contract) -> None:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


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
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL

# Archived complete imports; restore needed names in their original scope, not at this file tail.
