"""The settings file: the defaults, every field of ClassifierSettings, and a faulty file refused."""

import json
import tempfile
import unittest
from pathlib import Path

from arbol_classifier.errors import Failure
from arbol_classifier.settings import (
    DEFAULT_ENDPOINT,
    Settings,
    allowed_endpoint,
    exact_model,
    read_settings,
    settings_path,
)


class SettingsFile(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="arbol-classifier-settings-")
        self.addCleanup(temporary.cleanup)
        self.file = Path(temporary.name) / "arbol-classifier.json"

    def read(self, value: object) -> Settings:
        self.file.write_text(value if isinstance(value, str) else json.dumps(value), encoding="utf-8")
        return read_settings(self.file)

    def refused(self, value: object, *names: str, hidden: str | None = None) -> Failure:
        with self.assertRaises(Failure) as caught:
            self.read(value)
        failure = caught.exception
        self.assertEqual(failure.code, "invalid_input")
        self.assertIn(str(self.file), str(failure))
        for name in names:
            self.assertIn(name, str(failure))
        if hidden is not None:
            self.assertNotIn(hidden, str(failure))
        return failure

    def test_the_file_lies_in_the_arbol_folder(self) -> None:
        self.assertEqual(settings_path("/Users/someone"), Path("/Users/someone/.arbol/arbol-classifier.json"))

    def test_a_missing_file_gives_the_defaults(self) -> None:
        settings = read_settings(self.file)
        self.assertEqual(settings, Settings())
        self.assertEqual(
            (settings.model, settings.timeout_seconds, settings.max_request_bytes, settings.endpoint),
            ("jev-1.13.0", 10.0, 64000, "https://api.typesafe.ai/v1/systemone"),
        )
        self.assertIsNone(settings.secret_command)
        self.assertEqual(self.read({}), Settings())

    def test_every_field_is_read(self) -> None:
        settings = self.read(
            {
                "model": "jev-2.10.3",
                "timeoutSeconds": 2.5,
                "maxRequestBytes": 1000,
                "endpoint": "http://127.0.0.1:8649/v1/systemone",
                "secret": {"from": "command", "command": ["/usr/bin/printf", "key"]},
            }
        )
        self.assertEqual(
            settings, Settings("jev-2.10.3", 2.5, 1000, "http://127.0.0.1:8649/v1/systemone", ("/usr/bin/printf", "key"))
        )
        self.assertEqual(self.read({"timeoutSeconds": 60}).timeout_seconds, 60.0)
        self.assertIsNone(self.read({"secret": {"from": "keychain"}}).secret_command)

    def test_a_file_that_cannot_be_read_as_settings(self) -> None:
        for text in ("{", "", "[]", "null", '"jev-1.13.0"', '{"timeoutSeconds": NaN}', '{"timeoutSeconds": Infinity}'):
            with self.subTest(text=text):
                self.refused(text)
        self.file.write_bytes(b'{"model": "\xff"}')
        with self.assertRaises(Failure):
            read_settings(self.file)
        self.file.unlink()
        self.file.mkdir()
        with self.assertRaises(Failure) as caught:
            read_settings(self.file)
        self.assertIn(str(self.file), str(caught.exception))

    def test_an_unknown_key_refuses_the_file(self) -> None:
        # CLS-D5, by its proposed default: refuse the file and name the key.
        self.refused({"timoutSeconds": 5}, "timoutSeconds")
        self.refused({"model": "jev-1.13.0", "extra": 1, "more": 2}, "extra", "more")
        self.refused({"secret": {"from": "keychain", "account": "jev"}}, "secret.account")
        self.refused({"secret": {"from": "command", "command": ["/usr/bin/true"], "env": {}}}, "secret.env")

    def test_a_name_that_moves_is_refused_as_model(self) -> None:
        for model in ("jev-latest", "jev-preview", "jev-1.13", "jev-1.13.0-preview", "Jev-1.13.0", "jev-01.13.0", ""):
            with self.subTest(model=model):
                self.refused({"model": model}, "model", hidden=model or None)
        self.refused({"model": 1.13}, "model")

    def test_faulty_fields_are_named_without_their_values(self) -> None:
        cases: list[tuple[object, str, str | None]] = [
            ({"timeoutSeconds": "10"}, "timeoutSeconds", None),
            ({"timeoutSeconds": 0}, "timeoutSeconds", None),
            ({"timeoutSeconds": 0.5}, "timeoutSeconds", None),
            ({"timeoutSeconds": 61}, "timeoutSeconds", None),
            ({"timeoutSeconds": True}, "timeoutSeconds", None),
            ('{"timeoutSeconds": 1e400}', "timeoutSeconds", None),
            ({"maxRequestBytes": 0}, "maxRequestBytes", None),
            ({"maxRequestBytes": -1}, "maxRequestBytes", None),
            ({"maxRequestBytes": 1.5}, "maxRequestBytes", None),
            ({"maxRequestBytes": 64000.0}, "maxRequestBytes", None),
            ({"maxRequestBytes": True}, "maxRequestBytes", None),
            ({"endpoint": "https://example.com/v1/systemone"}, "endpoint", "example.com"),
            ({"endpoint": 5}, "endpoint", None),
            ({"secret": "keychain"}, "secret", None),
            ({"secret": {}}, "secret.from", None),
            ({"secret": {"from": "plain-file-marker"}}, "secret.from", "plain-file-marker"),
            ({"secret": {"from": "command"}}, "secret.command", None),
            ({"secret": {"from": "command", "command": []}}, "secret.command", None),
            ({"secret": {"from": "command", "command": ["", "print-key"]}}, "secret.command", "print-key"),
            ({"secret": {"from": "command", "command": ["/bin/key", 5]}}, "secret.command", "/bin/key"),
            ({"secret": {"from": "command", "command": "print-key-marker"}}, "secret.command", "print-key-marker"),
        ]
        for value, name, hidden in cases:
            with self.subTest(value=value):
                self.refused(value, name, hidden=hidden)


class Addresses(unittest.TestCase):
    def test_exact_versions(self) -> None:
        for model in ("jev-1.13.0", "jev-0.0.0", "jev-2.10.3", "jev-10.0.12"):
            self.assertTrue(exact_model(model), model)
        for model in ("jev-latest", "jev-1.13", "jev-1.13.0.1", "jev-1.13.0 ", "jev-١.13.0", "jev-1.13.00"):
            self.assertFalse(exact_model(model), model)

    def test_only_jev_or_this_mac(self) -> None:
        for endpoint in (
            DEFAULT_ENDPOINT,
            "http://localhost/v1/systemone",
            "https://localhost:8443/v1/systemone",
            "http://LOCALHOST:9/x",
            "http://127.0.0.1:8649/v1/systemone",
            "http://127.1.2.3/",
            "http://[::1]:7000/v1/systemone",
        ):
            self.assertTrue(allowed_endpoint(endpoint), endpoint)
        for endpoint in (
            "http://api.typesafe.ai/v1/systemone",
            "https://api.typesafe.ai/v2/systemone",
            "https://api.typesafe.ai/v1/systemone/",
            "https://example.com/v1/systemone",
            "http://192.168.1.20:8080/v1/systemone",
            "http://0.0.0.0/",
            "http://[::]/",
            "http://127.0.0.1.example.net/v1",
            "http://localhost@example.org/v1",
            "http://localhost.example.org/v1",
            "ftp://localhost/v1",
            "file:///tmp/x",
            "localhost:8080",
            "http://localhost:99999/",
            "http://localhost:port/",
            "http://localhost/\nx",
            "http://local host/",
            "",
        ):
            self.assertFalse(allowed_endpoint(endpoint), endpoint)
