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
import socket
import tempfile

from jev_stand_in import DROP, Received, Reply, StandIn, like_jev


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
    info = contract.info()
    expect(info["name"] == NAME, f"name is {info['name']!r}")
    expect(info["version"] == contract.version, f"version is {info['version']!r}, not {contract.version!r}")
    expect(info["build"] == contract.build, f"build is {info['build']!r}, not {contract.build!r}")
    expect(info["contract"] == 1 and type(info["contract"]) is int, f"contract is {info['contract']!r}")
    expect(info["keyFound"] is False, f"keyFound is {info['keyFound']!r}")


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


@scenario("classify.what-is-sent")
def classify_what_is_sent(contract: Contract) -> None:
    with StandIn() as stand_in:
        settings = contract.classify_settings(stand_in)
        request = choice_request()
        contract.answered(request, settings, stand_in)
        received = expect_sent(stand_in, request)
        headers = {name.lower(): value for name, value in received.headers}
        expect(len(headers) == len(received.headers), f"a header was sent twice: {received.headers}")
        expected = {"host": stand_in.url.split("/")[2], "accept-encoding": "identity",
                    "content-length": str(len(received.body)), "content-type": "application/json",
                    "authorization": f"Bearer {KEY}", "user-agent": NAME}
        expect(headers == expected, f"the headers sent are {received.headers}")
        expect(set(received.json()) == {"state", "questions", "model"}, "the body holds more than request and model")
        sent = json.dumps(received.headers) + received.body.decode("utf-8")
        for value in {socket.gethostname(), socket.gethostname().split(".")[0], str(contract.home),
                      str(contract.work)}:
            expect(not value or value not in sent, f"the request names the machine: {value!r}")


@scenario("classify.other-model")
def classify_other_model(contract: Contract) -> None:
    with StandIn() as stand_in:
        settings = contract.classify_settings(stand_in)
        for model in ("jev-1.14.0", "jev-latest", None):
            def other(received: Received, model: str | None = model) -> Reply:
                answers = {name: {"type": "choice", "choice": "request"} for name in received.json()["questions"]}
                reply: dict[str, Any] = {"answers": answers, "usage": {"input_tokens": 1, "output_tokens": 1}}
                if model is not None:
                    reply["model"] = model
                return Reply.of(reply)

            stand_in.script = other
            contract.classify_failed(choice_request(), settings, stand_in, "vendor_error", (DEFAULT_MODEL,), sends=1)


@scenario("classify.missing-answer")
def classify_missing_answer(contract: Contract) -> None:
    with StandIn() as stand_in:
        settings = contract.classify_settings(stand_in)
        request = {"state": JUDGED, "questions": {"work": {"type": "noul", "instructions": "Work?"},
                                                  "polite": {"type": "noul", "instructions": "Polite?"}}}
        answer = {"type": "noul", "noul": 0.5}
        for reply in (
            Reply.of({"model": DEFAULT_MODEL, "answers": {"work": answer}}),
            Reply.of({"model": DEFAULT_MODEL, "answers": {"work": answer, "polite": answer, "other": answer}}),
            Reply.of({"model": DEFAULT_MODEL, "answers": {}}),
            Reply.of({"model": DEFAULT_MODEL}),
            Reply.of({"model": DEFAULT_MODEL, "answers": [answer, answer]}),
            Reply.of([{"model": DEFAULT_MODEL}]),
            Reply(200, b"not JSON"),
        ):
            def scripted(received: Received, reply: Reply = reply) -> Reply:
                return reply

            stand_in.script = scripted
            contract.classify_failed(request, settings, stand_in, "vendor_error", sends=1)


@scenario("classify.size-limit")
def classify_size_limit(contract: Contract) -> None:
    with StandIn() as stand_in:
        request = choice_request()
        contract.answered(request, contract.classify_settings(stand_in), stand_in)
        size = len(stand_in.received[-1].body)
        exact = contract.classify_settings(stand_in, maxRequestBytes=size)
        contract.answered(request, exact, stand_in)
        expect_sent(stand_in, request)
        contract.classify_failed(request, contract.classify_settings(stand_in, maxRequestBytes=size - 1), stand_in,
                                 "invalid_input", (str(size), str(size - 1)))
        pretty = json.dumps(request, indent=8).encode("utf-8")
        expect(len(pretty) > size, "the pretty request is not larger than the body sent")
        contract.answered(pretty, contract.classify_settings(stand_in, maxRequestBytes=size), stand_in)
        expect_sent(stand_in, request)
        large = {**request, "state": JUDGED + " " + "long " * 12800}
        contract.classify_failed(large, contract.classify_settings(stand_in), stand_in, "invalid_input", ("64000",))


@scenario("classify.endpoint-elsewhere")
def classify_endpoint_elsewhere(contract: Contract) -> None:
    marker = contract.work / "key-command-ran"
    for endpoint in ("https://example.com/v1/systemone", "http://192.168.1.20:8080/v1/systemone",
                     "https://api.typesafe.ai/v2/systemone", "http://api.typesafe.ai/v1/systemone"):
        settings = contract.work / "elsewhere.json"
        settings.write_text(json.dumps({"endpoint": endpoint, "secret": {"from": "command",
                                        "command": ["/usr/bin/touch", str(marker)]}}), encoding="utf-8")
        error = failed(contract.classify(choice_request(), settings), ["classify"], "invalid_input",
                       (str(settings), "endpoint"), (endpoint,))
        expect(not marker.exists(), f"the key command ran for the endpoint {endpoint}: {error}")


@scenario("classify.writes-nothing")
def classify_writes_nothing(contract: Contract) -> None:
    temporary = contract.work / "tmp"
    temporary.mkdir()
    before = snapshot(contract.build_folder)
    expect(list(contract.home.iterdir()) == [], "the home folder is not empty before the calls")
    with StandIn() as stand_in:
        settings = contract.classify_settings(stand_in)
        environment = {"TMPDIR": str(temporary)}
        for request in (choice_request(), {"state": JUDGED, "questions": {"work": {"type": "noul",
                                                                                   "instructions": "Work?"}}}):
            outcome = contract.classify(request, settings, env=environment)
            expect(outcome.status == 0, f"classify ended with status {outcome.status}: {outcome.stdout}")
        stand_in.script = lambda received: Reply.of({"model": "jev-9.9.9", "answers": {}})
        failed(contract.classify(choice_request(), settings, env=environment), ["classify"], "vendor_error", (), ())
        failed(contract.classify({"state": JUDGED}, settings, env=environment), ["classify"], "invalid_input", (), ())
        expect(len(stand_in.received) == 3, f"three calls sent {len(stand_in.received)} requests, not 3")
    expect(list(contract.home.iterdir()) == [], f"a call left files in the home folder: {list(contract.home.iterdir())}")
    expect(list(temporary.iterdir()) == [], "a call left files in the temporary folder")
    expect(snapshot(contract.build_folder) == before, "the calls changed the Build's folder")


def bearer(received: Received) -> str | None:
    return next((value for name, value in received.headers if name.lower() == "authorization"), None)


def security_args(contract: Contract) -> list[list[str]]:
    return [call["args"] for call in contract.security.calls()]


@scenario("key.not-found")
def key_not_found(contract: Contract) -> None:
    """No key: no item, an empty item, an item that cannot be read, a key command that fails or prints nothing."""
    with StandIn() as stand_in:
        keychain = contract.keychain_settings(stand_in)
        failing = contract.keychain_settings(stand_in, "failing.json", secret={"from": "command",
                                                                              "command": ["/usr/bin/false"]})
        silent = contract.keychain_settings(stand_in, "silent.json", secret={"from": "command",
                                                                            "command": ["/usr/bin/true"]})
        where = f"the command that the settings file {failing} names for the key"
        cases: list[tuple[str, Callable[[], None], Path, tuple[str, ...]]] = [
            ("no item", lambda: None, keychain, (NO_KEY + ".",)),
            ("an empty item", lambda: contract.security.put(SERVICE, ACCOUNT, ""), keychain,
             (NO_KEY, "the item is empty")),
            ("an item that cannot be read", lambda: contract.security.fail(51), keychain,
             (NO_KEY, "could not be read")),
            ("a key command that fails", lambda: contract.security.fail(None), failing, (where, "failed")),
            ("a key command that prints nothing", lambda: None, silent,
             (f"the command that the settings file {silent} names for the key", "printed nothing")),
        ]
        for case, prepare, settings, names in cases:
            prepare()
            error = contract.classify_failed(choice_request(), settings, stand_in, "not_signed_in", names)
            expect(error["message"].startswith("No Jev API key was found."), f"{case}: {error['message']}")
            expect(STORE in str(error.get("remedy")), f"{case}: the remedy does not say how to store the key: {error}")
            expect(contract.info("--settings", str(settings))["keyFound"] is False, f"{case}: info found a key")
        expect(stand_in.received == [], "the stand-in for Jev received a request without a key")
    expect(contract.security.value(SERVICE, ACCOUNT) == "", "a call changed the item")


@scenario("key.only-in-the-bearer-token")
def key_only_in_the_bearer_token(contract: Contract) -> None:
    """The key appears in no output, diagnostic, argument, environment or settings file: only in the bearer token."""
    contract.security.put(SERVICE, ACCOUNT, KEY)
    with StandIn() as stand_in:
        settings = contract.keychain_settings(stand_in)
        contract.answered(choice_request(), settings, stand_in)
        contract.info("--settings", str(settings))
        contract.classify_failed({"state": JUDGED}, settings, stand_in, "invalid_input")
        stand_in.script = lambda received: Reply.of({"model": "jev-9.9.9", "answers": {}, "echo": bearer(received)})
        contract.classify_failed(choice_request(), settings, stand_in, "vendor_error", sends=1)
        stand_in.script = lambda received: Reply.of({"error": f"refused {bearer(received)}"}, 401)
        contract.classify_failed(choice_request(), settings, stand_in, "credential_rejected", sends=1)
        expect(len(stand_in.received) == 3, f"the stand-in for Jev received {len(stand_in.received)} requests, not 3")
        for received in stand_in.received:
            expect(bearer(received) == f"Bearer {KEY}", "a request did not carry the key as its bearer token")
            elsewhere = [received.method, received.path, received.body.decode("utf-8")] + [
                f"{name}: {value}" for name, value in received.headers if name.lower() != "authorization"]
            expect_no_key(json.dumps(elsewhere), "a request to Jev outside its bearer token")
    for call in contract.security.calls():
        expect_no_key(json.dumps([call["args"], call["env"]]), "an argument or the environment of security")
    expect_no_key(settings.read_text(encoding="utf-8"), "the settings file")


@scenario("add-key.at-a-terminal")
def add_key_at_a_terminal(contract: Contract) -> None:
    """add-key stores what was typed at the terminal; info then finds it, classify sends it; a second one replaces it."""
    outcome, shown = contract.at_terminal("add-key", typed=TYPED.encode() + b"\n")
    expect(outcome.status == 0, f"add-key ended with status {outcome.status}: {outcome.stdout}")
    expect(outcome.document == {"keychain": {"service": SERVICE, "account": ACCOUNT}, "replaced": False},
           f"add-key printed {outcome.stdout}")
    expect(b"Jev API key" in shown, "add-key did not ask at the terminal")
    expect(contract.security.value(SERVICE, ACCOUNT) == TYPED, "the stand-in for security did not receive the key")
    calls = contract.security.calls()
    expect(any(TYPED in call["stdin"] for call in calls), "the key did not reach security on its standard input")
    for call in calls:
        expect_no_key(json.dumps([call["args"], call["env"]]), "an argument or the environment of security")
    expect(contract.info()["keyFound"] is True, "info did not find the key that add-key stored")
    with StandIn() as stand_in:
        settings = contract.keychain_settings(stand_in)
        contract.answered(choice_request(), settings, stand_in)
        expect(bearer(stand_in.received[-1]) == f"Bearer {TYPED}", "classify did not send the key that add-key stored")
        outcome, _ = contract.at_terminal("add-key", typed=TYPED_SECOND.encode() + b"\r")
        expect(outcome.status == 0 and outcome.document.get("replaced") is True,
               f"the second add-key did not say that it replaced the key: {outcome.stdout}")
        expect(contract.security.value(SERVICE, ACCOUNT) == TYPED_SECOND, "the second add-key did not replace the key")
        contract.answered(choice_request(), settings, stand_in)
        expect(bearer(stand_in.received[-1]) == f"Bearer {TYPED_SECOND}", "classify did not send the replaced key")
    commands = [word for call in contract.security.calls() for word in call["args"] + call["stdin"].split()]
    expect("delete-generic-password" not in commands, "add-key removed the item")


@scenario("add-key.no-terminal")
def add_key_no_terminal(contract: Contract) -> None:
    """Without a terminal add-key refuses, and takes no key from standard input."""
    outcome = contract.call("add-key", data=TYPED.encode() + b"\n")
    error = failed(outcome, ["add-key"], "invalid_input", ("at a terminal", "Nothing was stored"), ())
    expect("there is none" in error["message"], f"the refusal does not say there is no terminal: {error}")
    expect(contract.security.calls() == [], "add-key without a terminal started security")


@scenario("cli.build-entry")
def cli_build_entry(contract: Contract) -> None:
    """The Build's own entry, bin/arbol-classifier, without the stand-in for security: a key command gives the key."""
    with StandIn() as stand_in:
        settings = contract.classify_settings(stand_in)
        info = contract.call("info", "--settings", str(settings), entry=True)
        expect(info.status == 0 and info.document.get("keyFound") is True and info.stderr == "",
               f"the Build's entry did not answer info: {info.stdout}")
        outcome = contract.call("classify", "--settings", str(settings), data=json.dumps(choice_request()).encode(),
                                entry=True)
        expect(outcome.status == 0 and outcome.document == json.loads(stand_in.replies[-1].body),
               f"the Build's entry did not answer classify: {outcome.stdout}")
        expect(bearer(stand_in.received[-1]) == f"Bearer {KEY}", "the Build's entry did not send the key")
        failed(contract.call("judge", entry=True), ["judge"], "invalid_input", (), ())


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


@scenario("errors.invalid-at-jev")
def errors_invalid_at_jev(contract: Contract) -> None:
    """422 and 413: invalid_input, with what Jev said, and never the judged text that Jev echoed."""
    echoed = {"detail": [{"loc": ["body", "questions", "kind", "criteria"], "msg": "Field required",
                          "type": "missing", "input": JUDGED}]}
    with StandIn() as stand_in:
        settings = contract.classify_settings(stand_in)
        for reply, status, names in (
            (Reply.of(echoed, 422), 422, ("body.questions.kind.criteria: Field required",)),
            (Reply.of({"detail": f"Too many tokens in {JUDGED}"}, 422), 422, ("Too many tokens in",)),
            (Reply(422, b"<html>Unprocessable</html>"), 422, ("gave no reason",)),
            (Reply.of({"message": "Request entity too large"}, 413), 413, ("too large", "Request entity too large")),
        ):
            stand_in.script = answering(reply)
            error = contract.classify_failed(choice_request(), settings, stand_in, "invalid_input", names, sends=1,
                                             scale=QUICK)
            vendor_status(error, status)


@scenario("errors.rate-limited")
def errors_rate_limited(contract: Contract) -> None:
    with StandIn(answering(Reply.of({"message": "Slow down"}, 429, (("Retry-After", "7"),)))) as stand_in:
        settings = contract.classify_settings(stand_in)
        error = contract.classify_failed(choice_request(), settings, stand_in, "rate_limited",
                                         ("429", "Attempts made: 3", "Slow down"), sends=3, scale=QUICK)
        vendor_status(error, 429)
        expect(error.get("retryAfterSeconds") == 7, f"the error does not name the time Jev named: {error}")
        stand_in.script = answering(Reply.of({}, 429))
        error = contract.classify_failed(choice_request(), settings, stand_in, "rate_limited", sends=3, scale=QUICK)
        expect("retryAfterSeconds" not in error, f"the error names a time Jev did not name: {error}")


@scenario("errors.vendor-unavailable")
def errors_vendor_unavailable(contract: Contract) -> None:
    """529, a status from 500 on, a connection closed without an answer, and an address where nothing listens."""
    with StandIn() as stand_in:
        settings = contract.classify_settings(stand_in)
        for status in (529, 500, 503):
            stand_in.script = answering(Reply.of({"message": "Busy"}, status))
            error = contract.classify_failed(choice_request(), settings, stand_in, "vendor_unavailable",
                                             (str(status), "Attempts made: 3"), sends=3, scale=QUICK)
            vendor_status(error, status)
        stand_in.script = answering(DROP)
        contract.classify_failed(choice_request(), settings, stand_in, "vendor_unavailable", ("Attempts made: 3",),
                                 sends=3, scale=QUICK)
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    nowhere = contract.work / "nowhere.json"
    key_file = contract.work / "key.txt"
    nowhere.write_text(json.dumps({"endpoint": f"http://127.0.0.1:{port}/v1/systemone",
                                   "secret": {"from": "command", "command": ["/bin/cat", str(key_file)]}}))
    failed(contract.classify(choice_request(), nowhere, scale=QUICK), ["classify"], "vendor_unavailable",
           ("could not be reached", "Attempts made: 3"), ())


@scenario("attempts.until-an-answer")
def attempts_until_an_answer(contract: Contract) -> None:
    """A further attempt after 529, 429, a status from 500 on or a closed connection, and the answer it brings."""
    with StandIn() as stand_in:
        settings = contract.classify_settings(stand_in)
        for replies in ((Reply.of({}, 529), Reply.of({}, 429), None), (DROP, None), (Reply.of({}, 502), None)):
            stand_in.script = answering(*replies)
            sent = len(stand_in.received)
            outcome = contract.classify(choice_request(), settings, scale=QUICK)
            expect(outcome.status == 0, f"classify ended with status {outcome.status}: {outcome.stdout}")
            expect(len(stand_in.received) - sent == len(replies),
                   f"classify made {len(stand_in.received) - sent} attempts, not {len(replies)}")
            expect(outcome.document == json.loads(stand_in.replies[-1].body), "classify did not print the answer")
        stand_in.script = answering(Reply.of({}, 529), Reply.of({"message": "No"}, 401))
        contract.classify_failed(choice_request(), settings, stand_in, "credential_rejected", sends=2, scale=QUICK)


@scenario("limits.time-limit")
def limits_time_limit(contract: Contract) -> None:
    """A Jev that does not answer, a slow key command and a request that does not end: limit_reached in time."""
    scale = 0.05
    with StandIn() as stand_in:
        stand_in.script = stand_in.hold(Reply.of({}))
        for seconds, args, fields in ((10, (), {}), (2, ("--timeout", "2"), {}), (4, (), {"timeoutSeconds": 4})):
            settings = contract.classify_settings(stand_in, **fields)
            outcome = contract.classify(choice_request(), settings, *args, scale=scale)
            failed(outcome, ["classify"], "limit_reached", (f"{seconds} seconds", "while Jev was asked"), ())
            expect(seconds * scale <= outcome.seconds < seconds * scale + 2,
                   f"a limit of {seconds} s, scaled to {seconds * scale} s, ended the call after {outcome.seconds:.2f} s")
        # An answer that comes one byte every 20 ms: every read gets something, but the whole would take 8 s.
        stand_in.script = answering(Reply(200, b" " * 400, drip=0.02))
        outcome = contract.classify(choice_request(), contract.classify_settings(stand_in), "--timeout", "2",
                                    scale=scale)
        failed(outcome, ["classify"], "limit_reached", ("2 seconds", "while Jev was asked"), ())
        expect(outcome.seconds < 0.1 + 2, f"an answer that came slowly held the call for {outcome.seconds:.2f} s")
        sent = len(stand_in.received)
        slow = contract.work / "slow-key.json"
        slow.write_text(json.dumps({"endpoint": stand_in.url, "secret": {"from": "command",
                                                                          "command": ["/bin/sleep", "30"]}}))
        outcome = contract.classify(choice_request(), slow, "--timeout", "2", scale=scale)
        failed(outcome, ["classify"], "limit_reached", ("2 seconds", "names for the key"), ())
        expect(outcome.seconds < 0.1 + 2, f"a slow key command held the call for {outcome.seconds:.2f} s")
        expect(len(stand_in.received) == sent, "classify asked Jev without a key")
        command = contract.command("classify", "--settings", str(contract.classify_settings(stand_in)), "--timeout",
                                   "2", scale=scale)
        started = time.monotonic()
        # Standard input stays open until the program has ended: the request never ends.
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   cwd=contract.home, env=contract.environment(), start_new_session=True)
        assert process.stdin is not None and process.stdout is not None and process.stderr is not None
        try:
            process.stdin.write(b'{"state": "a request that does not end')
            process.stdin.flush()
            process.wait(timeout=30)
            took = time.monotonic() - started
            out, err = process.stdout.read(), process.stderr.read()
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            for stream in (process.stdin, process.stdout, process.stderr):
                stream.close()
        outcome = contract.outcome(["classify"], process.returncode, out, err, took)
        failed(outcome, ["classify"], "limit_reached", ("while the request was read",), ())
        expect(outcome.seconds < 0.1 + 2, f"a request that did not end held the call for {outcome.seconds:.2f} s")
        expect(len(stand_in.received) == sent, "classify asked Jev before the request ended")


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
            work = base / f"work-{index}"
            work.mkdir()
            contract = Contract(program, build_folder, version, build, home, work,
                                SecurityStandIn(work / "security", str(build_folder / "runtime/python/bin/python3.14")))
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
        contract = Contract(program, build_folder, version, build, home, base / "work-quiet",
                            SecurityStandIn(base / "work-quiet/security", str(build_folder / "runtime/python/bin/python3.14")))
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

# Archived complete imports; restore needed names in their original scope, not at this file tail.
