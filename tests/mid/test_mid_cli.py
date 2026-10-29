"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_cli as _support
from test_cli import (
    ACCOUNT,
    Deadline,
    Failure,
    Invocation,
    Path,
    ROOT,
    SERVICE,
    cli,
    dumps,
    expected_identity,
    json,
    os,
    patch,
    security_stand_in,
    subprocess,
    sys,
    tempfile,
    unittest,
)


class Invocation(_support.Invocation):
# TEST-TIER-BEGIN tests/test_cli.py::Invocation.test_info_reports_identity_settings_and_no_key
    def test_info_reports_identity_settings_and_no_key(self) -> None:
        status, document = cli.run(["info"], self.environ)
        self.assertEqual(status, 0)
        version, build = expected_identity()
        self.assertEqual(
            document,
            {
                "name": "arbol-classifier",
                "version": version,
                "build": build,
                "contract": 1,
                "settingsFile": str(self.home / ".arbol/arbol-classifier.json"),
                "model": "jev-1.13.0",
                "endpoint": "https://api.typesafe.ai/v1/systemone",
                "keyFound": False,
            },
        )
# TEST-TIER-END tests/test_cli.py::Invocation.test_info_reports_identity_settings_and_no_key

# TEST-TIER-BEGIN tests/test_cli.py::Invocation.test_info_says_whether_a_key_was_found_never_the_key
    def test_info_says_whether_a_key_was_found_never_the_key(self) -> None:
        self.security.put(SERVICE, ACCOUNT, "key-marker-item")
        status, document = cli.run(["info"], self.environ)
        self.assertEqual((status, document["keyFound"]), (0, True))
        self.assertNotIn("key-marker", dumps(document))
        (self.home / "command.json").write_text('{"secret": {"from": "command", "command": ["/usr/bin/false"]}}')
        status, document = cli.run(["info", "--settings", str(self.home / "command.json")], self.environ)
        self.assertEqual((status, document["keyFound"]), (0, False))
# TEST-TIER-END tests/test_cli.py::Invocation.test_info_says_whether_a_key_was_found_never_the_key

# TEST-TIER-BEGIN tests/test_cli.py::Invocation.test_add_key_stores_what_was_typed
    def test_add_key_stores_what_was_typed(self) -> None:
        status, document = cli.run(["add-key"], self.environ, ask=lambda: " key-marker-typed\r\n")
        self.assertEqual(
            (status, document),
            (0, {"keychain": {"service": "com.sylvan-stack.arbol.classifier", "account": "jev"}, "replaced": False}),
        )
        self.assertEqual(self.security.value(SERVICE, ACCOUNT), "key-marker-typed")
        status, document = cli.run(["add-key"], self.environ, ask=lambda: "key-marker-second\n")
        self.assertEqual((status, document["replaced"]), (0, True))
        self.assertEqual(self.security.value(SERVICE, ACCOUNT), "key-marker-second")
        self.assertEqual(list(self.home.iterdir()), [])
# TEST-TIER-END tests/test_cli.py::Invocation.test_add_key_stores_what_was_typed

# TEST-TIER-BEGIN tests/test_cli.py::Invocation.test_add_key_refuses_what_cannot_be_a_key
    def test_add_key_refuses_what_cannot_be_a_key(self) -> None:
        for typed, says in (("", "No key was typed"), ("\n", "No key was typed"),
                            ("key-marker with space\n", "cannot be a Jev API key")):
            def ask(typed: str = typed) -> str:
                return typed

            status, document = cli.run(["add-key"], self.environ, ask=ask)
            error = document["error"]
            assert isinstance(error, dict)
            self.assertEqual((status, error["code"]), (1, "invalid_input"))
            self.assertIn(says, str(error["message"]))
            self.assertIn("Nothing was stored", str(error["message"]))
            self.assertNotIn("key-marker", dumps(document))
        self.assertEqual(self.security.calls(), [])
# TEST-TIER-END tests/test_cli.py::Invocation.test_add_key_refuses_what_cannot_be_a_key

# TEST-TIER-BEGIN tests/test_cli.py::Invocation.test_add_key_takes_no_options_and_no_arguments
    def test_add_key_takes_no_options_and_no_arguments(self) -> None:
        def ask() -> str:
            raise AssertionError("add-key asked for the key")

        for args in (["add-key", "--settings", "other.json"], ["add-key", "--timeout", "5"], ["add-key", "now"]):
            status, document = cli.run(args, self.environ, ask=ask)
            error = document["error"]
            assert isinstance(error, dict)
            self.assertEqual((status, error["code"]), (1, "invalid_input"))
# TEST-TIER-END tests/test_cli.py::Invocation.test_add_key_takes_no_options_and_no_arguments

# TEST-TIER-BEGIN tests/test_cli.py::Invocation.test_info_reads_the_named_settings_file
    def test_info_reads_the_named_settings_file(self) -> None:
        other = self.home / "other.json"
        other.write_text('{"model": "jev-1.14.0", "endpoint": "http://localhost:9/v1/systemone"}')
        with patch.object(os, "getcwd", return_value=str(self.home)):
            status, document = cli.run(["info", "--settings", "other.json"], self.environ)
        self.assertEqual(status, 0)
        self.assertEqual(
            (document["settingsFile"], document["model"], document["endpoint"]),
            (str(other), "jev-1.14.0", "http://localhost:9/v1/systemone"),
        )
# TEST-TIER-END tests/test_cli.py::Invocation.test_info_reads_the_named_settings_file

# TEST-TIER-BEGIN tests/test_cli.py::Invocation.test_refusals_are_error_objects
    def test_refusals_are_error_objects(self) -> None:
        (self.home / ".arbol").mkdir()
        (self.home / ".arbol/arbol-classifier.json").write_text('{"model": "jev-latest"}')
        for args in (["info"], [], ["judge"], ["info", "--verbose"], ["classify", "--timeout", "0"]):
            with self.subTest(args=args):
                status, document = cli.run(args, self.environ)
                self.assertEqual(status, 1)
                self.assertEqual(set(document), {"error"})
                error = document["error"]
                assert isinstance(error, dict)
                self.assertEqual((error["code"], error["retryable"]), ("invalid_input", False))
                self.assertIsInstance(error["message"], str)
# TEST-TIER-END tests/test_cli.py::Invocation.test_refusals_are_error_objects

# TEST-TIER-BEGIN tests/test_cli.py::Invocation.test_classify_reads_the_request_on_standard_input
    def test_classify_reads_the_request_on_standard_input(self) -> None:
        (self.home / ".arbol").mkdir()
        (self.home / ".arbol/arbol-classifier.json").write_text(
            '{"endpoint": "http://127.0.0.1:9/v1/systemone", "secret": {"from": "command", "command": ["/bin/echo", "k"]}}'
        )
        request = b'{"state": "judged marker", "questions": {"work": {"type": "noul", "instructions": "Work?"}}}'
        sent: list[tuple[str, bytes, str, float]] = []

        def send(endpoint: str, body: bytes, key: str, deadline: Deadline) -> tuple[int, bytes, int | None]:
            sent.append((endpoint, body, key, deadline.seconds))
            return 200, b'{"model": "jev-1.13.0", "answers": {"work": {"type": "noul", "noul": 1}}}', None

        def given(deadline: Deadline) -> bytes:
            return request

        with patch("arbol_classifier.classify.post", send):
            status, document = cli.run(["classify", "--timeout", "3"], self.environ, given)
            self.assertEqual((status, document["model"]), (0, "jev-1.13.0"))
            self.assertEqual([(call[0], call[2], call[3]) for call in sent], [("http://127.0.0.1:9/v1/systemone", "k", 3.0)])
            status, document = cli.run(["classify"], self.environ, given)
            self.assertEqual((status, sent[-1][3]), (0, 10.0))
# TEST-TIER-END tests/test_cli.py::Invocation.test_classify_reads_the_request_on_standard_input

# TEST-TIER-BEGIN tests/test_cli.py::Invocation.test_standard_input_is_read_until_it_ends_or_the_time_limit
    def test_standard_input_is_read_until_it_ends_or_the_time_limit(self) -> None:
        reading, writing = os.pipe()
        self.addCleanup(os.close, reading)
        os.write(writing, b'{"state": "judged marker",')
        os.write(writing, b' "questions": {}}')
        os.close(writing)
        with os.fdopen(os.dup(reading), "rb", buffering=0) as stdin, patch("sys.stdin", stdin):
            self.assertEqual(cli.standard_input(Deadline(10)), b'{"state": "judged marker", "questions": {}}')
        still_open, writer = os.pipe()
        self.addCleanup(os.close, still_open)
        self.addCleanup(os.close, writer)
        with (
            os.fdopen(os.dup(still_open), "rb", buffering=0) as stdin,
            patch("sys.stdin", stdin),
            patch("arbol_classifier.limits.SCALE", 0.05),
            self.assertRaises(Failure) as caught,
        ):
            cli.standard_input(Deadline(2))
        self.assertEqual(caught.exception.code, "limit_reached")
        self.assertIn("2 seconds", str(caught.exception))
# TEST-TIER-END tests/test_cli.py::Invocation.test_standard_input_is_read_until_it_ends_or_the_time_limit

# TEST-TIER-BEGIN tests/test_cli.py::Invocation.test_only_classify_reads_standard_input
    def test_only_classify_reads_standard_input(self) -> None:
        def unreadable(deadline: Deadline) -> bytes:
            raise AssertionError("standard input was read")

        self.assertEqual(cli.run(["info"], self.environ, unreadable)[0], 0)
        self.assertEqual(cli.run(["classify", "--timeout", "0"], self.environ, unreadable)[0], 1)
# TEST-TIER-END tests/test_cli.py::Invocation.test_only_classify_reads_standard_input

# TEST-TIER-BEGIN tests/test_cli.py::Invocation.test_a_refused_request_is_an_error_object
    def test_a_refused_request_is_an_error_object(self) -> None:
        for data in (b"", b"[]", b'{"state": "judged marker"}'):
            with self.subTest(data=data):
                status, document = cli.run(["classify"], self.environ, lambda deadline: data)  # noqa: B023
                self.assertEqual(status, 1)
                error = document["error"]
                assert isinstance(error, dict)
                self.assertEqual(error["code"], "invalid_input")
                self.assertNotIn("judged marker", dumps(document))
# TEST-TIER-END tests/test_cli.py::Invocation.test_a_refused_request_is_an_error_object

# TEST-TIER-BEGIN tests/test_cli.py::Invocation.test_an_unexpected_defect_is_internal
    def test_an_unexpected_defect_is_internal(self) -> None:
        with patch.object(cli, "read_settings", side_effect=RuntimeError("judged text marker")), patch("sys.stderr"):
            status, document = cli.run(["info"], self.environ)
        self.assertEqual(status, 1)
        self.assertNotIn("judged text marker", dumps(document))
        error = document["error"]
        assert isinstance(error, dict)
        self.assertEqual(error["code"], "internal")
# TEST-TIER-END tests/test_cli.py::Invocation.test_an_unexpected_defect_is_internal

# TEST-TIER-BEGIN tests/test_cli.py::Invocation.test_the_program_prints_one_json_document
    def test_the_program_prints_one_json_document(self) -> None:
        # The program starts the real /usr/bin/security for the Keychain item; a key command keeps it away.
        settings = self.home / "command.json"
        settings.write_text('{"secret": {"from": "command", "command": ["/usr/bin/true"]}}')
        for args, expected in ((["info", "--settings", str(settings)], 0), (["unknown"], 1)):
            result = subprocess.run(
                [sys.executable, "-I", "-B", str(ROOT / "bin/entry.py"), *args],
                env={"HOME": str(self.home), "PATH": "/usr/bin:/bin", "LANG": "C"},
                capture_output=True,
                check=False,
                timeout=60,
            )
            self.assertEqual(result.returncode, expected)
            self.assertEqual(result.stdout.count(b"\n"), 1)
            self.assertIsInstance(json.loads(result.stdout), dict)
            self.assertEqual(result.stderr, b"")
        self.assertEqual(list(self.home.iterdir()), [settings])
# TEST-TIER-END tests/test_cli.py::Invocation.test_the_program_prints_one_json_document
