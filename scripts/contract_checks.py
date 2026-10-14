"""The contract check of CLS-0: start the built program as a program and read what it prints.

Each scenario runs the Build's own program with a fresh home folder and checks its
standard output, its standard error and its exit status. From SYL-152 on it covers
`info`, the settings file and the refusals of the command line (CLS-0.14). From SYL-157
on it covers `classify` against the stand-in for Jev, which records what it was sent.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jev_stand_in import Received, Reply, StandIn

NAME = "arbol-classifier"
CODES = ("invalid_input", "not_signed_in", "credential_rejected", "rate_limited", "vendor_unavailable",
         "vendor_error", "limit_reached", "internal")
DEFAULT_MODEL = "jev-1.13.0"
DEFAULT_ENDPOINT = "https://api.typesafe.ai/v1/systemone"
INFO_FIELDS = {"name", "version", "build", "contract", "settingsFile", "model", "endpoint", "keyFound"}
KEY = "contract-check-key-5c1e"  # given by the key command of the test settings; not a Jev key
JUDGED = "Judged text marker: can you also update the README while you are at it?"


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
    work: Path  # beside the home folder: the test settings for classify and the file the key command prints

    def call(self, *args: str, cwd: Path | None = None, data: bytes | None = None,
             env: dict[str, str] | None = None) -> Outcome:
        result = subprocess.run([str(self.program), *args], cwd=cwd or self.home, input=data or b"",
                                env={"HOME": str(self.home), "PATH": "/usr/bin:/bin", "LANG": "C", **(env or {})},
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

    def classify(self, request: object, settings: Path, *args: str, env: dict[str, str] | None = None) -> Outcome:
        """One classify call. Neither the judged text nor the key may appear in what it prints."""
        data = request if isinstance(request, bytes) else json.dumps(request).encode("utf-8")
        outcome = self.call("classify", "--settings", str(settings), *args, data=data, env=env)
        for value, what in ((JUDGED, "the judged text"), (KEY, "the key")):
            expect(value not in outcome.stdout and value not in outcome.stderr, f"classify printed {what}")
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
                        names: tuple[str, ...] = (), sends: int = 0) -> dict[str, Any]:
        sent = len(stand_in.received)
        error = failed(self.classify(request, settings), ["classify"], code, names, ())
        expect(len(stand_in.received) == sent + sends,
               f"classify sent {len(stand_in.received) - sent} requests before it ended with {code}, not {sends}")
        return error


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
    with StandIn() as stand_in:
        settings = contract.classify_settings(stand_in)
        request = choice_request()
        result = contract.answered(request, settings, stand_in)
        expect_sent(stand_in, request)
        expect(result["answers"]["kind"]["choice"] == "request" and result["model"] == DEFAULT_MODEL,
               f"the choice is not passed on: {result}")
        contract.answered(request, settings, stand_in, "--timeout", "5")
        expect_sent(stand_in, request)


@scenario("classify.noul")
def classify_noul(contract: Contract) -> None:
    with StandIn() as stand_in:
        settings = contract.classify_settings(stand_in)
        request = {"state": {"message": JUDGED, "from": "the Leather Bag"},
                   "questions": {"work": {"type": "noul", "instructions": "Does the message ask for work?"},
                                 "polite": {"type": "noul", "instructions": "Is it polite?",
                                            "criteria": {"true": "It is polite", "false": "It is rude"}}}}
        result = contract.answered(request, settings, stand_in)
        expect_sent(stand_in, request)
        expect(set(result["answers"]) == {"work", "polite"} and result["answers"]["work"]["noul"] == 0.93,
               f"the answers are not passed on: {result}")


@scenario("classify.score")
def classify_score(contract: Contract) -> None:
    with StandIn() as stand_in:
        settings = contract.classify_settings(stand_in)
        request = {"state": [JUDGED, "and a second message"],
                   "questions": {"urgency": {"type": "score", "instructions": {"ask": "How urgent is it?"},
                                             "criteria": ["Not urgent", {"level": "Soon"}, "At once"]}}}
        result = contract.answered(request, settings, stand_in)
        expect_sent(stand_in, request)
        expect(result["answers"]["urgency"]["score"] == 2 and result["answers"]["urgency"]["legend"]["1"]
               == {"level": "Soon"}, f"the score is not passed on: {result}")


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


@scenario("classify.pinned-model")
def classify_pinned_model(contract: Contract) -> None:
    with StandIn() as stand_in:
        request = choice_request()
        contract.answered(request, contract.classify_settings(stand_in), stand_in)
        expect_sent(stand_in, request, DEFAULT_MODEL)
        result = contract.answered(request, contract.classify_settings(stand_in, model="jev-1.14.0"), stand_in)
        expect_sent(stand_in, request, "jev-1.14.0")
        expect(result["model"] == "jev-1.14.0", f"the result names {result['model']!r}")


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


@scenario("classify.names-a-model")
def classify_names_a_model(contract: Contract) -> None:
    with StandIn() as stand_in:
        settings = contract.classify_settings(stand_in)
        for model in (DEFAULT_MODEL, "jev-latest", None, ["jev-1.13.0"]):
            contract.classify_failed({**choice_request(), "model": model}, settings, stand_in, "invalid_input",
                                     ("model",))


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


@scenario("classify.malformed")
def classify_malformed(contract: Contract) -> None:
    question = {"type": "noul", "instructions": "Work?"}
    with StandIn() as stand_in:
        settings = contract.classify_settings(stand_in)
        for request in (
            b"", b"{", b"[]", b'"text"', b"null", b"5", b"{} {}", b"\xff\xfe", b'{"state": NaN, "questions": {}}',
            {"questions": {"work": question}},
            {"state": JUDGED},
            {"state": JUDGED, "questions": {}},
            {"state": JUDGED, "questions": [question]},
            {"state": JUDGED, "questions": {"work": "Does it ask for work?"}},
            {"state": JUDGED, "questions": {"work": {"instructions": "Work?"}}},
            {"state": JUDGED, "questions": {"work": {"type": "noul"}}},
            {"state": JUDGED, "questions": {"work": question, "polite": {"type": "noul"}}},
        ):
            contract.classify_failed(request, settings, stand_in, "invalid_input")


@scenario("classify.passes-questions-through")
def classify_passes_questions_through(contract: Contract) -> None:
    with StandIn() as stand_in:
        settings = contract.classify_settings(stand_in)
        request = {"state": None, "questions": {
            "order": {"type": "rank", "instructions": None, "hint": {"any": ["data"]}},
            "kind": {"type": "choice", "instructions": [], "criteria": {}},
        }, "trace": {"kept": True}}
        contract.answered(request, settings, stand_in)
        expect_sent(stand_in, request)


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
            contract = Contract(program, build_folder, version, build, home, work)
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
        contract = Contract(program, build_folder, version, build, home, base / "work-quiet")
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
