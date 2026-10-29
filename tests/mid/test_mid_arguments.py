"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_arguments as _support
from test_arguments import (
    Arguments,
    Failure,
    parse_arguments,
    unittest,
)


class Arguments(_support.Arguments):
# TEST-TIER-BEGIN tests/test_arguments.py::Arguments.test_timeout_takes_one_to_sixty_seconds
    def test_timeout_takes_one_to_sixty_seconds(self) -> None:
        for text, expected in (("1", 1.0), ("60", 60.0), ("10.25", 10.25), ("060", 60.0)):
            with self.subTest(text=text):
                self.assertEqual(parse_arguments(["classify", "--timeout", text]).timeout_seconds, expected)
        for text in ("0", "0.99", "60.01", "61", "-5", "ten", "1e1", " 5", "5 ", "５", "inf", "nan", "5."):
            with self.subTest(text=text):
                self.assertIn("--timeout", str(self.refused("classify", "--timeout", text)))
                self.assertIn("--timeout", str(self.refused("classify", f"--timeout={text}")))
# TEST-TIER-END tests/test_arguments.py::Arguments.test_timeout_takes_one_to_sixty_seconds

# TEST-TIER-BEGIN tests/test_arguments.py::Arguments.test_missing_and_unknown_commands
    def test_missing_and_unknown_commands(self) -> None:
        self.refused()
        self.refused("--settings", "a.json")
        failure = self.refused("judge-this-marker")
        self.assertNotIn("judge-this-marker", str(failure))
        self.refused("Info")
        self.refused("info", "extra")
# TEST-TIER-END tests/test_arguments.py::Arguments.test_missing_and_unknown_commands

# TEST-TIER-BEGIN tests/test_arguments.py::Arguments.test_unknown_options_and_build_selection
    def test_unknown_options_and_build_selection(self) -> None:
        for args in (
            ("info", "--verbose"),
            ("info", "--state-dir", "/tmp"),
            ("info", "-h"),
            ("info", "--"),
            ("-v", "3", "info"),
            ("info", "-v", "3"),
        ):
            with self.subTest(args=args):
                self.refused(*args)
        self.assertNotIn("secret-marker", str(self.refused("--key=secret-marker", "info")))
# TEST-TIER-END tests/test_arguments.py::Arguments.test_unknown_options_and_build_selection

# TEST-TIER-BEGIN tests/test_arguments.py::Arguments.test_option_values_are_required_and_given_once
    def test_option_values_are_required_and_given_once(self) -> None:
        self.refused("info", "--settings")
        self.refused("info", "--settings=")
        self.refused("info", "--settings", "--settings")
        self.refused("classify", "--timeout")
        self.refused("info", "--settings", "a", "--settings", "b")
        self.refused("classify", "--timeout", "5", "--timeout=6")
# TEST-TIER-END tests/test_arguments.py::Arguments.test_option_values_are_required_and_given_once
