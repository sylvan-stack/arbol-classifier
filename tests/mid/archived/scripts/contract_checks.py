# Mid-tier source from scripts/contract_checks.py; see MID_TIER.md.
# Shared helpers and refusal entry points remain at the original path.

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::info.identity
# @scenario("info.identity")
# def info_identity(contract: Contract) -> None:
#     info = contract.info()
#     expect(info["name"] == NAME, f"name is {info['name']!r}")
#     expect(info["version"] == contract.version, f"version is {info['version']!r}, not {contract.version!r}")
#     expect(info["build"] == contract.build, f"build is {info['build']!r}, not {contract.build!r}")
#     expect(info["contract"] == 1 and type(info["contract"]) is int, f"contract is {info['contract']!r}")
#     expect(info["keyFound"] is False, f"keyFound is {info['keyFound']!r}")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::info.identity

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::info.defaults
# @scenario("info.defaults")
# def info_defaults(contract: Contract) -> None:
#     info = contract.info()
#     expect(info["settingsFile"] == str(contract.home / ".arbol/arbol-classifier.json"),
#            f"settingsFile is {info['settingsFile']!r}")
#     expect(info["model"] == DEFAULT_MODEL, f"model is {info['model']!r}")
#     expect(info["endpoint"] == DEFAULT_ENDPOINT, f"endpoint is {info['endpoint']!r}")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::info.defaults

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::info.settings-file
# @scenario("info.settings-file")
# def info_settings_file(contract: Contract) -> None:
#     file = contract.settings({"model": "jev-1.14.0", "timeoutSeconds": 5, "maxRequestBytes": 32000,
#                               "endpoint": "http://127.0.0.1:8649/v1/systemone", "secret": {"from": "keychain"}})
#     info = contract.info()
#     expect(info["settingsFile"] == str(file), f"settingsFile is {info['settingsFile']!r}")
#     expect(info["model"] == "jev-1.14.0", f"model is {info['model']!r}")
#     expect(info["endpoint"] == "http://127.0.0.1:8649/v1/systemone", f"endpoint is {info['endpoint']!r}")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::info.settings-file

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::info.settings-option
# @scenario("info.settings-option")
# def info_settings_option(contract: Contract) -> None:
#     contract.settings({"model": "jev-1.14.0"})
#     other = contract.settings({"model": "jev-2.0.0", "endpoint": "http://localhost:9/v1/systemone"}, "tests/other.json")
#     for args in (("--settings", "tests/other.json"), (f"--settings={other}",)):
#         info = contract.info(*args, cwd=contract.home)
#         expect(info["settingsFile"] == str(other), f"settingsFile is {info['settingsFile']!r} for {list(args)}")
#         expect(info["model"] == "jev-2.0.0" and info["endpoint"] == "http://localhost:9/v1/systemone",
#                f"info did not read {other} for {list(args)}")
#     missing = contract.home / "tests/missing.json"
#     info = contract.info("--settings", str(missing))
#     expect(info["settingsFile"] == str(missing) and info["model"] == DEFAULT_MODEL,
#            "a missing settings file named with --settings did not give the defaults")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::info.settings-option

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::info.accepted-settings
# @scenario("info.accepted-settings")
# def info_accepted_settings(contract: Contract) -> None:
#     for value in (
#         {},
#         {"model": "jev-2.10.3", "timeoutSeconds": 2.5, "maxRequestBytes": 1, "endpoint": "http://[::1]:7000/v1/systemone",
#          "secret": {"from": "command", "command": ["/usr/bin/true"]}},
#         {"timeoutSeconds": 1, "endpoint": "https://localhost/v1/systemone"},
#         {"timeoutSeconds": 60, "endpoint": DEFAULT_ENDPOINT, "secret": {"from": "keychain"}},
#     ):
#         contract.settings(value)
#         info = contract.info()
#         expect(info["model"] == value.get("model", DEFAULT_MODEL), f"model is {info['model']!r} for {value}")
#         expect(info["endpoint"] == value.get("endpoint", DEFAULT_ENDPOINT), f"endpoint is {info['endpoint']!r}")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::info.accepted-settings

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::settings.faulty-file
# @scenario("settings.faulty-file")
# def settings_faulty_file(contract: Contract) -> None:
#     file = contract.home / ".arbol/arbol-classifier.json"
#     for text in ("{", "[]", '"jev-1.13.0"', "null", '{"timeoutSeconds": NaN}', ""):
#         contract.settings(text)
#         contract.refused("info", names=(str(file),))
#     file.unlink()
#     file.mkdir()
#     contract.refused("info", names=(str(file),))
# TEST-TIER-DISABLED-END scripts/contract_checks.py::settings.faulty-file

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::settings.unknown-key
# @scenario("settings.unknown-key")
# def settings_unknown_key(contract: Contract) -> None:
#     file = contract.settings({"timoutSeconds": 5})
#     contract.refused("info", names=(str(file), "timoutSeconds"))
#     contract.settings({"secret": {"from": "keychain", "account": "jev"}})
#     contract.refused("info", names=("secret.account",))
#     contract.settings({"secret": {"from": "command", "command": ["/usr/bin/true"], "env": {}}})
#     contract.refused("info", names=("secret.env",))
# TEST-TIER-DISABLED-END scripts/contract_checks.py::settings.unknown-key

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::settings.moving-model
# @scenario("settings.moving-model")
# def settings_moving_model(contract: Contract) -> None:
#     for model in ("jev-latest", "jev-preview", "jev-1.13", "jev-1.13.0-preview", "Jev-1.13.0", "jev-01.13.0"):
#         contract.settings({"model": model})
#         contract.refused("info", names=("model",), hidden=(model,))
# TEST-TIER-DISABLED-END scripts/contract_checks.py::settings.moving-model

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::settings.faulty-fields
# @scenario("settings.faulty-fields")
# def settings_faulty_fields(contract: Contract) -> None:
#     cases: list[tuple[object, str, tuple[str, ...]]] = [
#         ({"model": 5}, "model", ()),
#         ({"model": ""}, "model", ()),
#         ({"timeoutSeconds": "10"}, "timeoutSeconds", ()),
#         ({"timeoutSeconds": 0}, "timeoutSeconds", ()),
#         ({"timeoutSeconds": 0.5}, "timeoutSeconds", ()),
#         ({"timeoutSeconds": 61}, "timeoutSeconds", ()),
#         ({"timeoutSeconds": True}, "timeoutSeconds", ()),
#         ('{"timeoutSeconds": 1e400}', "timeoutSeconds", ()),
#         ({"maxRequestBytes": 0}, "maxRequestBytes", ()),
#         ({"maxRequestBytes": 1.5}, "maxRequestBytes", ()),
#         ({"maxRequestBytes": "64000"}, "maxRequestBytes", ()),
#         ({"maxRequestBytes": False}, "maxRequestBytes", ()),
#         ({"endpoint": "https://example.com/v1/systemone"}, "endpoint", ("example.com",)),
#         ({"endpoint": "https://api.typesafe.ai/v2/systemone"}, "endpoint", ("v2/systemone",)),
#         ({"endpoint": "http://192.168.1.20:8080/v1/systemone"}, "endpoint", ("192.168.1.20",)),
#         ({"endpoint": "http://127.0.0.1.example.net/v1"}, "endpoint", ("example.net",)),
#         ({"endpoint": "http://localhost@example.org/v1"}, "endpoint", ("example.org",)),
#         ({"endpoint": "ftp://localhost/v1"}, "endpoint", ("ftp:",)),
#         ({"endpoint": "localhost:8080"}, "endpoint", ("localhost:8080",)),
#         ({"endpoint": ["http://localhost/"]}, "endpoint", ()),
#         ({"secret": "keychain"}, "secret", ()),
#         ({"secret": {}}, "secret.from", ()),
#         ({"secret": {"from": "plain-file-marker"}}, "secret.from", ("plain-file-marker",)),
#         ({"secret": {"from": "command"}}, "secret.command", ()),
#         ({"secret": {"from": "command", "command": []}}, "secret.command", ()),
#         ({"secret": {"from": "command", "command": ["", "print-key"]}}, "secret.command", ("print-key",)),
#         ({"secret": {"from": "command", "command": "print-key-marker"}}, "secret.command", ("print-key-marker",)),
#     ]
#     for value, name, hidden in cases:
#         file = contract.settings(value)
#         contract.refused("info", names=(str(file), name), hidden=hidden)
# TEST-TIER-DISABLED-END scripts/contract_checks.py::settings.faulty-fields

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::cli.no-command
# @scenario("cli.no-command")
# def cli_no_command(contract: Contract) -> None:
#     contract.refused()
#     contract.refused("--settings", "tests/other.json")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::cli.no-command

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::cli.unknown-command
# @scenario("cli.unknown-command")
# def cli_unknown_command(contract: Contract) -> None:
#     for command in ("judge-this-marker", "Info", "help"):
#         contract.refused(command, hidden=(command,) if command != "help" else ())
# TEST-TIER-DISABLED-END scripts/contract_checks.py::cli.unknown-command

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::cli.unknown-option
# @scenario("cli.unknown-option")
# def cli_unknown_option(contract: Contract) -> None:
#     for args in (("info", "--verbose"), ("info", "--state-dir", "/tmp/state"), ("info", "-h"), ("info", "--"),
#                  ("--key=secret-marker", "info")):
#         contract.refused(*args, hidden=("secret-marker",))
# TEST-TIER-DISABLED-END scripts/contract_checks.py::cli.unknown-option

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::cli.build-selector
# @scenario("cli.build-selector")
# def cli_build_selector(contract: Contract) -> None:
#     contract.refused("-v", "3", "info")
#     contract.refused("info", "-v", "3")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::cli.build-selector

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::cli.extra-argument
# @scenario("cli.extra-argument")
# def cli_extra_argument(contract: Contract) -> None:
#     contract.refused("info", "now")
#     contract.refused("info", "classify")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::cli.extra-argument

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::cli.option-once
# @scenario("cli.option-once")
# def cli_option_once(contract: Contract) -> None:
#     contract.refused("info", "--settings", "a.json", "--settings", "b.json", names=("--settings",))
#     contract.refused("classify", "--timeout", "5", "--timeout=6", names=("--timeout",))
# TEST-TIER-DISABLED-END scripts/contract_checks.py::cli.option-once

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::cli.option-value
# @scenario("cli.option-value")
# def cli_option_value(contract: Contract) -> None:
#     contract.refused("info", "--settings", names=("--settings",))
#     contract.refused("info", "--settings=", names=("--settings",))
#     contract.refused("info", "--settings", "--settings", names=("--settings",))
#     contract.refused("classify", "--timeout", names=("--timeout",))
# TEST-TIER-DISABLED-END scripts/contract_checks.py::cli.option-value

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::cli.timeout
# @scenario("cli.timeout")
# def cli_timeout(contract: Contract) -> None:
#     contract.refused("info", "--timeout", "5", names=("--timeout",))
#     for value in ("0", "0.5", "61", "60.5", "ten", "-5", "1e1", " 5", "５"):
#         contract.refused("classify", "--timeout", value, names=("--timeout",))
#         contract.refused("classify", f"--timeout={value}", names=("--timeout",))
# TEST-TIER-DISABLED-END scripts/contract_checks.py::cli.timeout

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::classify.choice
# @scenario("classify.choice")
# def classify_choice(contract: Contract) -> None:
#     with StandIn() as stand_in:
#         settings = contract.classify_settings(stand_in)
#         request = choice_request()
#         result = contract.answered(request, settings, stand_in)
#         expect_sent(stand_in, request)
#         expect(result["answers"]["kind"]["choice"] == "request" and result["model"] == DEFAULT_MODEL,
#                f"the choice is not passed on: {result}")
#         contract.answered(request, settings, stand_in, "--timeout", "5")
#         expect_sent(stand_in, request)
# TEST-TIER-DISABLED-END scripts/contract_checks.py::classify.choice

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::classify.noul
# @scenario("classify.noul")
# def classify_noul(contract: Contract) -> None:
#     with StandIn() as stand_in:
#         settings = contract.classify_settings(stand_in)
#         request = {"state": {"message": JUDGED, "from": "the Leather Bag"},
#                    "questions": {"work": {"type": "noul", "instructions": "Does the message ask for work?"},
#                                  "polite": {"type": "noul", "instructions": "Is it polite?",
#                                             "criteria": {"true": "It is polite", "false": "It is rude"}}}}
#         result = contract.answered(request, settings, stand_in)
#         expect_sent(stand_in, request)
#         expect(set(result["answers"]) == {"work", "polite"} and result["answers"]["work"]["noul"] == 0.93,
#                f"the answers are not passed on: {result}")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::classify.noul

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::classify.score
# @scenario("classify.score")
# def classify_score(contract: Contract) -> None:
#     with StandIn() as stand_in:
#         settings = contract.classify_settings(stand_in)
#         request = {"state": [JUDGED, "and a second message"],
#                    "questions": {"urgency": {"type": "score", "instructions": {"ask": "How urgent is it?"},
#                                              "criteria": ["Not urgent", {"level": "Soon"}, "At once"]}}}
#         result = contract.answered(request, settings, stand_in)
#         expect_sent(stand_in, request)
#         expect(result["answers"]["urgency"]["score"] == 2 and result["answers"]["urgency"]["legend"]["1"]
#                == {"level": "Soon"}, f"the score is not passed on: {result}")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::classify.score

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::classify.what-is-sent
# @scenario("classify.what-is-sent")
# def classify_what_is_sent(contract: Contract) -> None:
#     with StandIn() as stand_in:
#         settings = contract.classify_settings(stand_in)
#         request = choice_request()
#         contract.answered(request, settings, stand_in)
#         received = expect_sent(stand_in, request)
#         headers = {name.lower(): value for name, value in received.headers}
#         expect(len(headers) == len(received.headers), f"a header was sent twice: {received.headers}")
#         expected = {"host": stand_in.url.split("/")[2], "accept-encoding": "identity",
#                     "content-length": str(len(received.body)), "content-type": "application/json",
#                     "authorization": f"Bearer {KEY}", "user-agent": NAME}
#         expect(headers == expected, f"the headers sent are {received.headers}")
#         expect(set(received.json()) == {"state", "questions", "model"}, "the body holds more than request and model")
#         sent = json.dumps(received.headers) + received.body.decode("utf-8")
#         for value in {socket.gethostname(), socket.gethostname().split(".")[0], str(contract.home),
#                       str(contract.work)}:
#             expect(not value or value not in sent, f"the request names the machine: {value!r}")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::classify.what-is-sent

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::classify.pinned-model
# @scenario("classify.pinned-model")
# def classify_pinned_model(contract: Contract) -> None:
#     with StandIn() as stand_in:
#         request = choice_request()
#         contract.answered(request, contract.classify_settings(stand_in), stand_in)
#         expect_sent(stand_in, request, DEFAULT_MODEL)
#         result = contract.answered(request, contract.classify_settings(stand_in, model="jev-1.14.0"), stand_in)
#         expect_sent(stand_in, request, "jev-1.14.0")
#         expect(result["model"] == "jev-1.14.0", f"the result names {result['model']!r}")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::classify.pinned-model

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::classify.other-model
# @scenario("classify.other-model")
# def classify_other_model(contract: Contract) -> None:
#     with StandIn() as stand_in:
#         settings = contract.classify_settings(stand_in)
#         for model in ("jev-1.14.0", "jev-latest", None):
#             def other(received: Received, model: str | None = model) -> Reply:
#                 answers = {name: {"type": "choice", "choice": "request"} for name in received.json()["questions"]}
#                 reply: dict[str, Any] = {"answers": answers, "usage": {"input_tokens": 1, "output_tokens": 1}}
#                 if model is not None:
#                     reply["model"] = model
#                 return Reply.of(reply)
#
#             stand_in.script = other
#             contract.classify_failed(choice_request(), settings, stand_in, "vendor_error", (DEFAULT_MODEL,), sends=1)
# TEST-TIER-DISABLED-END scripts/contract_checks.py::classify.other-model

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::classify.missing-answer
# @scenario("classify.missing-answer")
# def classify_missing_answer(contract: Contract) -> None:
#     with StandIn() as stand_in:
#         settings = contract.classify_settings(stand_in)
#         request = {"state": JUDGED, "questions": {"work": {"type": "noul", "instructions": "Work?"},
#                                                   "polite": {"type": "noul", "instructions": "Polite?"}}}
#         answer = {"type": "noul", "noul": 0.5}
#         for reply in (
#             Reply.of({"model": DEFAULT_MODEL, "answers": {"work": answer}}),
#             Reply.of({"model": DEFAULT_MODEL, "answers": {"work": answer, "polite": answer, "other": answer}}),
#             Reply.of({"model": DEFAULT_MODEL, "answers": {}}),
#             Reply.of({"model": DEFAULT_MODEL}),
#             Reply.of({"model": DEFAULT_MODEL, "answers": [answer, answer]}),
#             Reply.of([{"model": DEFAULT_MODEL}]),
#             Reply(200, b"not JSON"),
#         ):
#             def scripted(received: Received, reply: Reply = reply) -> Reply:
#                 return reply
#
#             stand_in.script = scripted
#             contract.classify_failed(request, settings, stand_in, "vendor_error", sends=1)
# TEST-TIER-DISABLED-END scripts/contract_checks.py::classify.missing-answer

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::classify.names-a-model
# @scenario("classify.names-a-model")
# def classify_names_a_model(contract: Contract) -> None:
#     with StandIn() as stand_in:
#         settings = contract.classify_settings(stand_in)
#         for model in (DEFAULT_MODEL, "jev-latest", None, ["jev-1.13.0"]):
#             contract.classify_failed({**choice_request(), "model": model}, settings, stand_in, "invalid_input",
#                                      ("model",))
# TEST-TIER-DISABLED-END scripts/contract_checks.py::classify.names-a-model

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::classify.size-limit
# @scenario("classify.size-limit")
# def classify_size_limit(contract: Contract) -> None:
#     with StandIn() as stand_in:
#         request = choice_request()
#         contract.answered(request, contract.classify_settings(stand_in), stand_in)
#         size = len(stand_in.received[-1].body)
#         exact = contract.classify_settings(stand_in, maxRequestBytes=size)
#         contract.answered(request, exact, stand_in)
#         expect_sent(stand_in, request)
#         contract.classify_failed(request, contract.classify_settings(stand_in, maxRequestBytes=size - 1), stand_in,
#                                  "invalid_input", (str(size), str(size - 1)))
#         pretty = json.dumps(request, indent=8).encode("utf-8")
#         expect(len(pretty) > size, "the pretty request is not larger than the body sent")
#         contract.answered(pretty, contract.classify_settings(stand_in, maxRequestBytes=size), stand_in)
#         expect_sent(stand_in, request)
#         large = {**request, "state": JUDGED + " " + "long " * 12800}
#         contract.classify_failed(large, contract.classify_settings(stand_in), stand_in, "invalid_input", ("64000",))
# TEST-TIER-DISABLED-END scripts/contract_checks.py::classify.size-limit

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::classify.malformed
# @scenario("classify.malformed")
# def classify_malformed(contract: Contract) -> None:
#     question = {"type": "noul", "instructions": "Work?"}
#     with StandIn() as stand_in:
#         settings = contract.classify_settings(stand_in)
#         for request in (
#             b"", b"{", b"[]", b'"text"', b"null", b"5", b"{} {}", b"\xff\xfe", b'{"state": NaN, "questions": {}}',
#             {"questions": {"work": question}},
#             {"state": JUDGED},
#             {"state": JUDGED, "questions": {}},
#             {"state": JUDGED, "questions": [question]},
#             {"state": JUDGED, "questions": {"work": "Does it ask for work?"}},
#             {"state": JUDGED, "questions": {"work": {"instructions": "Work?"}}},
#             {"state": JUDGED, "questions": {"work": {"type": "noul"}}},
#             {"state": JUDGED, "questions": {"work": question, "polite": {"type": "noul"}}},
#         ):
#             contract.classify_failed(request, settings, stand_in, "invalid_input")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::classify.malformed

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::classify.passes-questions-through
# @scenario("classify.passes-questions-through")
# def classify_passes_questions_through(contract: Contract) -> None:
#     with StandIn() as stand_in:
#         settings = contract.classify_settings(stand_in)
#         request = {"state": None, "questions": {
#             "order": {"type": "rank", "instructions": None, "hint": {"any": ["data"]}},
#             "kind": {"type": "choice", "instructions": [], "criteria": {}},
#         }, "trace": {"kept": True}}
#         contract.answered(request, settings, stand_in)
#         expect_sent(stand_in, request)
# TEST-TIER-DISABLED-END scripts/contract_checks.py::classify.passes-questions-through

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::classify.endpoint-elsewhere
# @scenario("classify.endpoint-elsewhere")
# def classify_endpoint_elsewhere(contract: Contract) -> None:
#     marker = contract.work / "key-command-ran"
#     for endpoint in ("https://example.com/v1/systemone", "http://192.168.1.20:8080/v1/systemone",
#                      "https://api.typesafe.ai/v2/systemone", "http://api.typesafe.ai/v1/systemone"):
#         settings = contract.work / "elsewhere.json"
#         settings.write_text(json.dumps({"endpoint": endpoint, "secret": {"from": "command",
#                                         "command": ["/usr/bin/touch", str(marker)]}}), encoding="utf-8")
#         error = failed(contract.classify(choice_request(), settings), ["classify"], "invalid_input",
#                        (str(settings), "endpoint"), (endpoint,))
#         expect(not marker.exists(), f"the key command ran for the endpoint {endpoint}: {error}")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::classify.endpoint-elsewhere

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::classify.writes-nothing
# @scenario("classify.writes-nothing")
# def classify_writes_nothing(contract: Contract) -> None:
#     temporary = contract.work / "tmp"
#     temporary.mkdir()
#     before = snapshot(contract.build_folder)
#     expect(list(contract.home.iterdir()) == [], "the home folder is not empty before the calls")
#     with StandIn() as stand_in:
#         settings = contract.classify_settings(stand_in)
#         environment = {"TMPDIR": str(temporary)}
#         for request in (choice_request(), {"state": JUDGED, "questions": {"work": {"type": "noul",
#                                                                                    "instructions": "Work?"}}}):
#             outcome = contract.classify(request, settings, env=environment)
#             expect(outcome.status == 0, f"classify ended with status {outcome.status}: {outcome.stdout}")
#         stand_in.script = lambda received: Reply.of({"model": "jev-9.9.9", "answers": {}})
#         failed(contract.classify(choice_request(), settings, env=environment), ["classify"], "vendor_error", (), ())
#         failed(contract.classify({"state": JUDGED}, settings, env=environment), ["classify"], "invalid_input", (), ())
#         expect(len(stand_in.received) == 3, f"three calls sent {len(stand_in.received)} requests, not 3")
#     expect(list(contract.home.iterdir()) == [], f"a call left files in the home folder: {list(contract.home.iterdir())}")
#     expect(list(temporary.iterdir()) == [], "a call left files in the temporary folder")
#     expect(snapshot(contract.build_folder) == before, "the calls changed the Build's folder")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::classify.writes-nothing

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::key.keychain
# @scenario("key.keychain")
# def key_keychain(contract: Contract) -> None:
#     """The key is read at each call from the Keychain item, with the system's command, and never written there."""
#     contract.security.put(SERVICE, ACCOUNT, KEY)
#     with StandIn() as stand_in:
#         settings = contract.keychain_settings(stand_in)
#         request = choice_request()
#         contract.answered(request, settings, stand_in)
#         expect(bearer(stand_in.received[-1]) == f"Bearer {KEY}", "classify did not send the key of the item")
#         contract.security.put(SERVICE, ACCOUNT, KEY_SECOND)
#         contract.answered(request, settings, stand_in)
#         expect(bearer(stand_in.received[-1]) == f"Bearer {KEY_SECOND}",
#                "classify did not read the item again at the second call")
#         expect(contract.info("--settings", str(settings))["keyFound"] is True, "info did not find the key of the item")
#     expect(security_args(contract) == [FIND, FIND, FIND],
#            f"the calls asked security for more than the item: {security_args(contract)}")
#     expect(contract.security.value(SERVICE, ACCOUNT) == KEY_SECOND, "a call changed the item")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::key.keychain

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::key.not-found
# @scenario("key.not-found")
# def key_not_found(contract: Contract) -> None:
#     """No key: no item, an empty item, an item that cannot be read, a key command that fails or prints nothing."""
#     with StandIn() as stand_in:
#         keychain = contract.keychain_settings(stand_in)
#         failing = contract.keychain_settings(stand_in, "failing.json", secret={"from": "command",
#                                                                               "command": ["/usr/bin/false"]})
#         silent = contract.keychain_settings(stand_in, "silent.json", secret={"from": "command",
#                                                                             "command": ["/usr/bin/true"]})
#         where = f"the command that the settings file {failing} names for the key"
#         cases: list[tuple[str, Callable[[], None], Path, tuple[str, ...]]] = [
#             ("no item", lambda: None, keychain, (NO_KEY + ".",)),
#             ("an empty item", lambda: contract.security.put(SERVICE, ACCOUNT, ""), keychain,
#              (NO_KEY, "the item is empty")),
#             ("an item that cannot be read", lambda: contract.security.fail(51), keychain,
#              (NO_KEY, "could not be read")),
#             ("a key command that fails", lambda: contract.security.fail(None), failing, (where, "failed")),
#             ("a key command that prints nothing", lambda: None, silent,
#              (f"the command that the settings file {silent} names for the key", "printed nothing")),
#         ]
#         for case, prepare, settings, names in cases:
#             prepare()
#             error = contract.classify_failed(choice_request(), settings, stand_in, "not_signed_in", names)
#             expect(error["message"].startswith("No Jev API key was found."), f"{case}: {error['message']}")
#             expect(STORE in str(error.get("remedy")), f"{case}: the remedy does not say how to store the key: {error}")
#             expect(contract.info("--settings", str(settings))["keyFound"] is False, f"{case}: info found a key")
#         expect(stand_in.received == [], "the stand-in for Jev received a request without a key")
#     expect(contract.security.value(SERVICE, ACCOUNT) == "", "a call changed the item")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::key.not-found

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::key.only-in-the-bearer-token
# @scenario("key.only-in-the-bearer-token")
# def key_only_in_the_bearer_token(contract: Contract) -> None:
#     """The key appears in no output, diagnostic, argument, environment or settings file: only in the bearer token."""
#     contract.security.put(SERVICE, ACCOUNT, KEY)
#     with StandIn() as stand_in:
#         settings = contract.keychain_settings(stand_in)
#         contract.answered(choice_request(), settings, stand_in)
#         contract.info("--settings", str(settings))
#         contract.classify_failed({"state": JUDGED}, settings, stand_in, "invalid_input")
#         stand_in.script = lambda received: Reply.of({"model": "jev-9.9.9", "answers": {}, "echo": bearer(received)})
#         contract.classify_failed(choice_request(), settings, stand_in, "vendor_error", sends=1)
#         stand_in.script = lambda received: Reply.of({"error": f"refused {bearer(received)}"}, 401)
#         contract.classify_failed(choice_request(), settings, stand_in, "credential_rejected", sends=1)
#         expect(len(stand_in.received) == 3, f"the stand-in for Jev received {len(stand_in.received)} requests, not 3")
#         for received in stand_in.received:
#             expect(bearer(received) == f"Bearer {KEY}", "a request did not carry the key as its bearer token")
#             elsewhere = [received.method, received.path, received.body.decode("utf-8")] + [
#                 f"{name}: {value}" for name, value in received.headers if name.lower() != "authorization"]
#             expect_no_key(json.dumps(elsewhere), "a request to Jev outside its bearer token")
#     for call in contract.security.calls():
#         expect_no_key(json.dumps([call["args"], call["env"]]), "an argument or the environment of security")
#     expect_no_key(settings.read_text(encoding="utf-8"), "the settings file")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::key.only-in-the-bearer-token

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::add-key.at-a-terminal
# @scenario("add-key.at-a-terminal")
# def add_key_at_a_terminal(contract: Contract) -> None:
#     """add-key stores what was typed at the terminal; info then finds it, classify sends it; a second one replaces it."""
#     outcome, shown = contract.at_terminal("add-key", typed=TYPED.encode() + b"\n")
#     expect(outcome.status == 0, f"add-key ended with status {outcome.status}: {outcome.stdout}")
#     expect(outcome.document == {"keychain": {"service": SERVICE, "account": ACCOUNT}, "replaced": False},
#            f"add-key printed {outcome.stdout}")
#     expect(b"Jev API key" in shown, "add-key did not ask at the terminal")
#     expect(contract.security.value(SERVICE, ACCOUNT) == TYPED, "the stand-in for security did not receive the key")
#     calls = contract.security.calls()
#     expect(any(TYPED in call["stdin"] for call in calls), "the key did not reach security on its standard input")
#     for call in calls:
#         expect_no_key(json.dumps([call["args"], call["env"]]), "an argument or the environment of security")
#     expect(contract.info()["keyFound"] is True, "info did not find the key that add-key stored")
#     with StandIn() as stand_in:
#         settings = contract.keychain_settings(stand_in)
#         contract.answered(choice_request(), settings, stand_in)
#         expect(bearer(stand_in.received[-1]) == f"Bearer {TYPED}", "classify did not send the key that add-key stored")
#         outcome, _ = contract.at_terminal("add-key", typed=TYPED_SECOND.encode() + b"\r")
#         expect(outcome.status == 0 and outcome.document.get("replaced") is True,
#                f"the second add-key did not say that it replaced the key: {outcome.stdout}")
#         expect(contract.security.value(SERVICE, ACCOUNT) == TYPED_SECOND, "the second add-key did not replace the key")
#         contract.answered(choice_request(), settings, stand_in)
#         expect(bearer(stand_in.received[-1]) == f"Bearer {TYPED_SECOND}", "classify did not send the replaced key")
#     commands = [word for call in contract.security.calls() for word in call["args"] + call["stdin"].split()]
#     expect("delete-generic-password" not in commands, "add-key removed the item")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::add-key.at-a-terminal

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::add-key.no-terminal
# @scenario("add-key.no-terminal")
# def add_key_no_terminal(contract: Contract) -> None:
#     """Without a terminal add-key refuses, and takes no key from standard input."""
#     outcome = contract.call("add-key", data=TYPED.encode() + b"\n")
#     error = failed(outcome, ["add-key"], "invalid_input", ("at a terminal", "Nothing was stored"), ())
#     expect("there is none" in error["message"], f"the refusal does not say there is no terminal: {error}")
#     expect(contract.security.calls() == [], "add-key without a terminal started security")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::add-key.no-terminal

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::add-key.not-a-key
# @scenario("add-key.not-a-key")
# def add_key_not_a_key(contract: Contract) -> None:
#     """Nothing typed, or something that cannot be a key: refused, and nothing is stored."""
#     for typed, says in ((b"\n", "No key was typed"), (b"\x04", "No key was typed"),
#                         (TYPED.encode() + b" and more\n", "cannot be a Jev API key")):
#         outcome, _ = contract.at_terminal("add-key", typed=typed)
#         failed(outcome, ["add-key"], "invalid_input", (says, "Nothing was stored"), ())
#     expect(contract.security.calls() == [], "add-key started security for something that is not a key")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::add-key.not-a-key

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::add-key.keychain-refuses
# @scenario("add-key.keychain-refuses")
# def add_key_keychain_refuses(contract: Contract) -> None:
#     """A Keychain that does not store the key: the call fails and says so, without the key."""
#     contract.security.fail(51)
#     outcome, _ = contract.at_terminal("add-key", typed=TYPED.encode() + b"\n")
#     failed(outcome, ["add-key"], "internal", ("could not be stored", SERVICE), ())
# TEST-TIER-DISABLED-END scripts/contract_checks.py::add-key.keychain-refuses

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::cli.add-key-arguments
# @scenario("cli.add-key-arguments")
# def cli_add_key_arguments(contract: Contract) -> None:
#     for args in (("add-key", "--settings", "other.json"), ("add-key", "--timeout", "5"), ("add-key", "now")):
#         contract.refused(*args)
#     expect(contract.security.calls() == [], "a refused add-key started security")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::cli.add-key-arguments

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::cli.build-entry
# @scenario("cli.build-entry")
# def cli_build_entry(contract: Contract) -> None:
#     """The Build's own entry, bin/arbol-classifier, without the stand-in for security: a key command gives the key."""
#     with StandIn() as stand_in:
#         settings = contract.classify_settings(stand_in)
#         info = contract.call("info", "--settings", str(settings), entry=True)
#         expect(info.status == 0 and info.document.get("keyFound") is True and info.stderr == "",
#                f"the Build's entry did not answer info: {info.stdout}")
#         outcome = contract.call("classify", "--settings", str(settings), data=json.dumps(choice_request()).encode(),
#                                 entry=True)
#         expect(outcome.status == 0 and outcome.document == json.loads(stand_in.replies[-1].body),
#                f"the Build's entry did not answer classify: {outcome.stdout}")
#         expect(bearer(stand_in.received[-1]) == f"Bearer {KEY}", "the Build's entry did not send the key")
#         failed(contract.call("judge", entry=True), ["judge"], "invalid_input", (), ())
# TEST-TIER-DISABLED-END scripts/contract_checks.py::cli.build-entry

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::errors.credential-rejected
# @scenario("errors.credential-rejected")
# def errors_credential_rejected(contract: Contract) -> None:
#     with StandIn(answering(Reply.of({"message": "Invalid API key"}, 401))) as stand_in:
#         settings = contract.classify_settings(stand_in)
#         error = contract.classify_failed(choice_request(), settings, stand_in, "credential_rejected",
#                                          ("401", "Invalid API key"), sends=1, scale=QUICK)
#         vendor_status(error, 401)
#         expect(STORE in str(error.get("remedy")), f"the remedy does not say how to store a key: {error}")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::errors.credential-rejected

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::errors.invalid-at-jev
# @scenario("errors.invalid-at-jev")
# def errors_invalid_at_jev(contract: Contract) -> None:
#     """422 and 413: invalid_input, with what Jev said, and never the judged text that Jev echoed."""
#     echoed = {"detail": [{"loc": ["body", "questions", "kind", "criteria"], "msg": "Field required",
#                           "type": "missing", "input": JUDGED}]}
#     with StandIn() as stand_in:
#         settings = contract.classify_settings(stand_in)
#         for reply, status, names in (
#             (Reply.of(echoed, 422), 422, ("body.questions.kind.criteria: Field required",)),
#             (Reply.of({"detail": f"Too many tokens in {JUDGED}"}, 422), 422, ("Too many tokens in",)),
#             (Reply(422, b"<html>Unprocessable</html>"), 422, ("gave no reason",)),
#             (Reply.of({"message": "Request entity too large"}, 413), 413, ("too large", "Request entity too large")),
#         ):
#             stand_in.script = answering(reply)
#             error = contract.classify_failed(choice_request(), settings, stand_in, "invalid_input", names, sends=1,
#                                              scale=QUICK)
#             vendor_status(error, status)
# TEST-TIER-DISABLED-END scripts/contract_checks.py::errors.invalid-at-jev

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::errors.rate-limited
# @scenario("errors.rate-limited")
# def errors_rate_limited(contract: Contract) -> None:
#     with StandIn(answering(Reply.of({"message": "Slow down"}, 429, (("Retry-After", "7"),)))) as stand_in:
#         settings = contract.classify_settings(stand_in)
#         error = contract.classify_failed(choice_request(), settings, stand_in, "rate_limited",
#                                          ("429", "Attempts made: 3", "Slow down"), sends=3, scale=QUICK)
#         vendor_status(error, 429)
#         expect(error.get("retryAfterSeconds") == 7, f"the error does not name the time Jev named: {error}")
#         stand_in.script = answering(Reply.of({}, 429))
#         error = contract.classify_failed(choice_request(), settings, stand_in, "rate_limited", sends=3, scale=QUICK)
#         expect("retryAfterSeconds" not in error, f"the error names a time Jev did not name: {error}")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::errors.rate-limited

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::errors.vendor-unavailable
# @scenario("errors.vendor-unavailable")
# def errors_vendor_unavailable(contract: Contract) -> None:
#     """529, a status from 500 on, a connection closed without an answer, and an address where nothing listens."""
#     with StandIn() as stand_in:
#         settings = contract.classify_settings(stand_in)
#         for status in (529, 500, 503):
#             stand_in.script = answering(Reply.of({"message": "Busy"}, status))
#             error = contract.classify_failed(choice_request(), settings, stand_in, "vendor_unavailable",
#                                              (str(status), "Attempts made: 3"), sends=3, scale=QUICK)
#             vendor_status(error, status)
#         stand_in.script = answering(DROP)
#         contract.classify_failed(choice_request(), settings, stand_in, "vendor_unavailable", ("Attempts made: 3",),
#                                  sends=3, scale=QUICK)
#     with socket.socket() as probe:
#         probe.bind(("127.0.0.1", 0))
#         port = probe.getsockname()[1]
#     nowhere = contract.work / "nowhere.json"
#     key_file = contract.work / "key.txt"
#     nowhere.write_text(json.dumps({"endpoint": f"http://127.0.0.1:{port}/v1/systemone",
#                                    "secret": {"from": "command", "command": ["/bin/cat", str(key_file)]}}))
#     failed(contract.classify(choice_request(), nowhere, scale=QUICK), ["classify"], "vendor_unavailable",
#            ("could not be reached", "Attempts made: 3"), ())
# TEST-TIER-DISABLED-END scripts/contract_checks.py::errors.vendor-unavailable

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::errors.vendor-error
# @scenario("errors.vendor-error")
# def errors_vendor_error(contract: Contract) -> None:
#     """Another refusal: no further attempt. A reply that cannot be accepted is checked in classify.other-model and
#     classify.missing-answer."""
#     with StandIn() as stand_in:
#         settings = contract.classify_settings(stand_in)
#         for status in (400, 403, 404, 302):
#             stand_in.script = answering(Reply.of({"message": "No"}, status))
#             error = contract.classify_failed(choice_request(), settings, stand_in, "vendor_error", (str(status),),
#                                              sends=1, scale=QUICK)
#             vendor_status(error, status)
# TEST-TIER-DISABLED-END scripts/contract_checks.py::errors.vendor-error

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::attempts.until-an-answer
# @scenario("attempts.until-an-answer")
# def attempts_until_an_answer(contract: Contract) -> None:
#     """A further attempt after 529, 429, a status from 500 on or a closed connection, and the answer it brings."""
#     with StandIn() as stand_in:
#         settings = contract.classify_settings(stand_in)
#         for replies in ((Reply.of({}, 529), Reply.of({}, 429), None), (DROP, None), (Reply.of({}, 502), None)):
#             stand_in.script = answering(*replies)
#             sent = len(stand_in.received)
#             outcome = contract.classify(choice_request(), settings, scale=QUICK)
#             expect(outcome.status == 0, f"classify ended with status {outcome.status}: {outcome.stdout}")
#             expect(len(stand_in.received) - sent == len(replies),
#                    f"classify made {len(stand_in.received) - sent} attempts, not {len(replies)}")
#             expect(outcome.document == json.loads(stand_in.replies[-1].body), "classify did not print the answer")
#         stand_in.script = answering(Reply.of({}, 529), Reply.of({"message": "No"}, 401))
#         contract.classify_failed(choice_request(), settings, stand_in, "credential_rejected", sends=2, scale=QUICK)
# TEST-TIER-DISABLED-END scripts/contract_checks.py::attempts.until-an-answer

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::attempts.waits
# @scenario("attempts.waits")
# def attempts_waits(contract: Contract) -> None:
#     """Half a second before the second attempt and one second before the third, here scaled by 0.1."""
#     with StandIn(answering(Reply.of({}, 529))) as stand_in:
#         settings = contract.classify_settings(stand_in)
#         contract.classify_failed(choice_request(), settings, stand_in, "vendor_unavailable", sends=3, scale=0.1)
#         first, second, third = (received.at for received in stand_in.received)
#         expect(0.05 <= second - first < 0.5, f"the first wait took {second - first:.3f} s, not 0.05 s")
#         expect(0.1 <= third - second < 0.55, f"the second wait took {third - second:.3f} s, not 0.1 s")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::attempts.waits

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::limits.no-wait-past-the-limit
# @scenario("limits.no-wait-past-the-limit")
# def limits_no_wait_past_the_limit(contract: Contract) -> None:
#     """Scaled by 0.2, a limit of 1.2 seconds is 0.24 s: it holds the first wait of 0.1 s but not the second of 0.2 s.
#     The call ends with what the last attempt gave, within its limit."""
#     with StandIn(answering(Reply.of({}, 529))) as stand_in:
#         settings = contract.classify_settings(stand_in)
#         outcome = contract.classify(choice_request(), settings, "--timeout", "1.2", scale=0.2)
#         failed(outcome, ["classify"], "vendor_unavailable", ("Attempts made: 2",), ())
#         expect(len(stand_in.received) == 2, f"classify made {len(stand_in.received)} attempts, not 2")
#         expect(stand_in.received[-1].at - stand_in.received[0].at < 0.24, "an attempt was made past the time limit")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::limits.no-wait-past-the-limit

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::limits.time-limit
# @scenario("limits.time-limit")
# def limits_time_limit(contract: Contract) -> None:
#     """A Jev that does not answer, a slow key command and a request that does not end: limit_reached in time."""
#     scale = 0.05
#     with StandIn() as stand_in:
#         stand_in.script = stand_in.hold(Reply.of({}))
#         for seconds, args, fields in ((10, (), {}), (2, ("--timeout", "2"), {}), (4, (), {"timeoutSeconds": 4})):
#             settings = contract.classify_settings(stand_in, **fields)
#             outcome = contract.classify(choice_request(), settings, *args, scale=scale)
#             failed(outcome, ["classify"], "limit_reached", (f"{seconds} seconds", "while Jev was asked"), ())
#             expect(seconds * scale <= outcome.seconds < seconds * scale + 2,
#                    f"a limit of {seconds} s, scaled to {seconds * scale} s, ended the call after {outcome.seconds:.2f} s")
#         # An answer that comes one byte every 20 ms: every read gets something, but the whole would take 8 s.
#         stand_in.script = answering(Reply(200, b" " * 400, drip=0.02))
#         outcome = contract.classify(choice_request(), contract.classify_settings(stand_in), "--timeout", "2",
#                                     scale=scale)
#         failed(outcome, ["classify"], "limit_reached", ("2 seconds", "while Jev was asked"), ())
#         expect(outcome.seconds < 0.1 + 2, f"an answer that came slowly held the call for {outcome.seconds:.2f} s")
#         sent = len(stand_in.received)
#         slow = contract.work / "slow-key.json"
#         slow.write_text(json.dumps({"endpoint": stand_in.url, "secret": {"from": "command",
#                                                                           "command": ["/bin/sleep", "30"]}}))
#         outcome = contract.classify(choice_request(), slow, "--timeout", "2", scale=scale)
#         failed(outcome, ["classify"], "limit_reached", ("2 seconds", "names for the key"), ())
#         expect(outcome.seconds < 0.1 + 2, f"a slow key command held the call for {outcome.seconds:.2f} s")
#         expect(len(stand_in.received) == sent, "classify asked Jev without a key")
#         command = contract.command("classify", "--settings", str(contract.classify_settings(stand_in)), "--timeout",
#                                    "2", scale=scale)
#         started = time.monotonic()
#         # Standard input stays open until the program has ended: the request never ends.
#         process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
#                                    cwd=contract.home, env=contract.environment(), start_new_session=True)
#         assert process.stdin is not None and process.stdout is not None and process.stderr is not None
#         try:
#             process.stdin.write(b'{"state": "a request that does not end')
#             process.stdin.flush()
#             process.wait(timeout=30)
#             took = time.monotonic() - started
#             out, err = process.stdout.read(), process.stderr.read()
#         finally:
#             if process.poll() is None:
#                 process.kill()
#                 process.wait()
#             for stream in (process.stdin, process.stdout, process.stderr):
#                 stream.close()
#         outcome = contract.outcome(["classify"], process.returncode, out, err, took)
#         failed(outcome, ["classify"], "limit_reached", ("while the request was read",), ())
#         expect(outcome.seconds < 0.1 + 2, f"a request that did not end held the call for {outcome.seconds:.2f} s")
#         expect(len(stand_in.received) == sent, "classify asked Jev before the request ended")
# TEST-TIER-DISABLED-END scripts/contract_checks.py::limits.time-limit

# TEST-TIER-DISABLED-BEGIN scripts/contract_checks.py::run_contract
# def run_contract(program: Path, build_folder: Path, version: str, build: str) -> int:
#     failed = 0
#     with tempfile.TemporaryDirectory(prefix="arbol-classifier-contract-") as name:
#         base = Path(name).resolve()
#         before = snapshot(build_folder)
#         for index, (title, function) in enumerate(SCENARIOS):
#             home = base / f"home-{index}"
#             home.mkdir()
#             work = base / f"work-{index}"
#             work.mkdir()
#             contract = Contract(program, build_folder, version, build, home, work,
#                                 SecurityStandIn(work / "security", str(build_folder / "runtime/python/bin/python3.14")))
#             try:
#                 function(contract)
#             except (ContractFailure, OSError, subprocess.TimeoutExpired, UnicodeDecodeError) as error:
#                 failed += 1
#                 print(f"FAILED {title}: {error}", flush=True)
#             else:
#                 print(f"passed {title}", flush=True)
#         title = "info.writes-nothing"
#         home = base / "home-quiet"
#         (home / ".arbol").mkdir(parents=True)
#         (home / ".arbol/arbol-classifier.json").write_text('{"model": "jev-1.14.0"}')
#         contract = Contract(program, build_folder, version, build, home, base / "work-quiet",
#                             SecurityStandIn(base / "work-quiet/security", str(build_folder / "runtime/python/bin/python3.14")))
#         quiet_before = snapshot(home)
#         try:
#             contract.info()
#             contract.refused("info", "--timeout", "5")
#             expect(snapshot(home) == quiet_before, "a call changed the home folder")
#             expect(snapshot(build_folder) == before, "the calls changed the Build's folder")
#         except (ContractFailure, OSError, subprocess.TimeoutExpired, UnicodeDecodeError) as error:
#             failed += 1
#             print(f"FAILED {title}: {error}", flush=True)
#         else:
#             print(f"passed {title}", flush=True)
#     total = len(SCENARIOS) + 1
#     print(json.dumps({"check": "contract", "scenarios": total, "passed": total - failed, "failed": failed}), flush=True)
#     return 1 if failed else 0
# TEST-TIER-DISABLED-END scripts/contract_checks.py::run_contract

# TEST-TIER-IMPORTS-BEGIN scripts/contract_checks.py:22
# import socket
# TEST-TIER-IMPORTS-END scripts/contract_checks.py:22

# TEST-TIER-IMPORTS-BEGIN scripts/contract_checks.py:24
# import tempfile
# TEST-TIER-IMPORTS-END scripts/contract_checks.py:24

# TEST-TIER-IMPORTS-BEGIN scripts/contract_checks.py:31
# from jev_stand_in import DROP, Received, Reply, StandIn, like_jev
# TEST-TIER-IMPORTS-END scripts/contract_checks.py:31

raise RuntimeError("Mid-tier checks require an explicitly requested testing task; see MID_TIER.md.")
