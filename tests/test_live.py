"""The live check (CLS-0.15): how it asks Jev one question, and what it takes as passed.

No test reaches Jev or the Keychain: a pretend program stands in for the Build's own, and where
the real program runs, the stand-in for `security` holds no item, so the call ends before
anything is sent.
"""

import contextlib
import io
import json
import os
import shlex
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from stand_ins import SecurityStandIn

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import live_check  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
INFO = {"name": "arbol-classifier", "version": "1.0.0", "build": "5", "contract": 1,
        "settingsFile": "/Users/someone/.arbol/arbol-classifier.json", "model": "jev-1.13.0",
        "endpoint": live_check.JEV, "keyFound": True}
REPLY: dict[str, Any] = {"model": "jev-1.13.0",
         "answers": {"kind": {"type": "choice", "choice": "request", "confidence": 1.0,
                              "probabilities": {"request": 1.0, "question": 0.0, "other": 0.0}}},
         "usage": {"input_tokens": 333, "output_tokens": 38}}
SET_BY_THE_SYSTEM = {"PWD", "OLDPWD", "SHLVL", "_", "__CF_USER_TEXT_ENCODING"}  # by /bin/sh and macOS, not passed on
NO_KEY = {"error": {"code": "not_signed_in", "message": "No Jev API key was found.", "retryable": False,
                    "remedy": "Store the key with: arbol-classifier add-key"}}
PRETEND = """
import json, os, sys
folder = os.path.dirname(os.path.abspath(sys.argv[0]))
answers = json.load(open(os.path.join(folder, "answers.json")))
with open(os.path.join(folder, "calls.jsonl"), "a") as log:
    log.write(json.dumps({"args": sys.argv[1:], "stdin": sys.stdin.read(), "env": dict(os.environ),
                          "cwd": os.getcwd()}) + "\\n")
status, document = answers[sys.argv[1]]
print(json.dumps(document))
sys.exit(status)
"""


class PretendBuild:
    """A Build folder whose `bin/arbol-classifier` prints given answers and records how it was started."""

    def __init__(self, folder: Path, answers: dict[str, tuple[int, dict[str, Any]]]) -> None:
        self.folder = folder
        (folder / "bin").mkdir()
        (folder / "pretend.py").write_text(PRETEND, encoding="utf-8")
        program = folder / "bin/arbol-classifier"
        program.write_text(f"#!/bin/sh\nexec {shlex.quote(sys.executable)} -I -B {shlex.quote(str(folder / 'pretend.py'))}"
                           ' "$@"\n', encoding="utf-8")
        program.chmod(0o755)
        (folder / "answers.json").write_text(json.dumps(answers), encoding="utf-8")

    def calls(self) -> list[dict[str, Any]]:
        log = self.folder / "calls.jsonl"
        return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []


class LiveTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="arbol-classifier-live-")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name)
        self.home = self.work / "home"
        self.home.mkdir()
        person = {"HOME": str(self.home), "USER": "someone", "LOGNAME": "someone", "PATH": "/usr/bin:/bin",
                  "LANG": "en_US.UTF-8"}
        replacement = patch.object(live_check, "environment", return_value=person)
        replacement.start()
        self.addCleanup(replacement.stop)
        switch = patch.dict(os.environ)
        switch.start()
        self.addCleanup(switch.stop)
        os.environ.pop(live_check.SECURITY_SWITCH, None)

    def build(self, answers: dict[str, tuple[int, dict[str, Any]]]) -> PretendBuild:
        folder = self.work / "build"
        folder.mkdir()
        return PretendBuild(folder, answers)

    def live(self, folder: Path) -> tuple[int, str]:
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            status = live_check.run_live(folder)
        return status, printed.getvalue()


class Judge(unittest.TestCase):
    def test_the_reply_names_the_model_of_info_and_holds_the_answer(self) -> None:
        said = live_check.judge(INFO, REPLY)
        self.assertIn("jev-1.13.0", said)
        self.assertIn("'request'", said)
        self.assertIn("333 of input, 38 of output", said)

    def test_a_reply_from_another_model_fails(self) -> None:
        with self.assertRaisesRegex(live_check.LiveFailure, "jev-1.14.0"):
            live_check.judge(INFO, {**REPLY, "model": "jev-1.14.0"})

    def test_a_reply_without_the_answer_fails(self) -> None:
        kind = REPLY["answers"]["kind"]
        for answers in ({}, {"kind": kind, "extra": kind}, {"kind": {**kind, "choice": "maybe"}},
                        {"kind": {**kind, "type": "noul"}}, {"kind": {**kind, "confidence": 1.5}},
                        {"kind": {**kind, "confidence": True}}):
            with self.subTest(answers=answers), self.assertRaises(live_check.LiveFailure):
                live_check.judge(INFO, {**REPLY, "answers": answers})

    def test_a_reply_without_usage_still_holds_the_answer(self) -> None:
        reply = {key: value for key, value in REPLY.items() if key != "usage"}
        self.assertIn("Jev reported no usage", live_check.judge(INFO, reply))


class Live(LiveTest):
    def test_one_choice_question_through_the_builds_own_program(self) -> None:
        build = self.build({"info": (0, INFO), "classify": (0, REPLY)})
        status, printed = self.live(build.folder)
        self.assertEqual(status, 0, printed)
        self.assertIn("live: passed", printed)
        self.assertIn("333 of input, 38 of output", printed)
        calls = build.calls()
        self.assertEqual([call["args"] for call in calls], [["info"], ["classify"]])
        self.assertEqual(json.loads(calls[1]["stdin"]), live_check.REQUEST)
        self.assertEqual(live_check.REQUEST["questions"]["kind"]["type"], "choice")

    def test_the_program_gets_the_persons_home_and_nothing_else_of_the_environment(self) -> None:
        build = self.build({"info": (0, INFO), "classify": (0, REPLY)})
        with patch.dict(os.environ, {"ARBOL_BUILD_DIR": str(build.folder), "SOMETHING_ELSE": "1"}):
            self.live(build.folder)
        for call in build.calls():
            environment = {name: value for name, value in call["env"].items() if name not in SET_BY_THE_SYSTEM}
            self.assertEqual(environment, live_check.environment())
            self.assertEqual(Path(call["cwd"]).resolve(), self.home.resolve())

    def test_without_a_key_it_fails_and_shows_the_programs_refusal(self) -> None:
        build = self.build({"info": (0, {**INFO, "keyFound": False}), "classify": (1, NO_KEY)})
        status, printed = self.live(build.folder)
        self.assertEqual(status, 1)
        self.assertIn("live: failed. `classify` ended with not_signed_in: No Jev API key was found.", printed)
        self.assertIn("Remedy: Store the key with: arbol-classifier add-key", printed)

    def test_a_stand_in_for_jev_cannot_pass(self) -> None:
        build = self.build({"info": (0, {**INFO, "endpoint": "http://127.0.0.1:8080/v1/systemone"}),
                            "classify": (0, REPLY)})
        status, printed = self.live(build.folder)
        self.assertEqual(status, 1)
        self.assertIn("the live check asks Jev itself", printed)
        self.assertEqual([call["args"] for call in build.calls()], [["info"]])

    def test_a_reply_that_is_not_one_json_object_fails(self) -> None:
        build = self.build({"info": (0, INFO), "classify": (0, [])})  # type: ignore[dict-item]
        status, printed = self.live(build.folder)
        self.assertEqual(status, 1)
        self.assertIn("did not print a JSON object", printed)

    def test_the_switch_must_name_an_executable_by_its_absolute_path(self) -> None:
        build = self.build({"info": (0, INFO), "classify": (0, REPLY)})
        for value in ("security", str(self.work / "missing")):
            with self.subTest(value=value), patch.dict(os.environ, {live_check.SECURITY_SWITCH: value}):
                status, printed = self.live(build.folder)
                self.assertEqual(status, 1)
                self.assertIn("absolute path", printed)
        self.assertEqual(build.calls(), [])


class WithoutAKey(LiveTest):
    """The real program, started as the live check starts it, with the stand-in for `security` holding no item."""

    def test_a_build_made_while_no_key_is_stored_fails_the_live_check(self) -> None:
        folder = self.work / "build"
        (folder / "runtime/python/bin").mkdir(parents=True)
        (folder / "runtime/python/bin/python3.14").symlink_to(sys.executable)
        (folder / "scripts").symlink_to(ROOT / "scripts")
        stand_in = SecurityStandIn(self.work / "security")
        with patch.dict(os.environ, {live_check.SECURITY_SWITCH: str(stand_in.program)}):
            status, printed = self.live(folder)
        self.assertEqual(status, 1, printed)
        self.assertIn(f"live: {stand_in.program} takes the place of /usr/bin/security", printed)
        self.assertIn("live: `info` found no Jev key", printed)
        self.assertIn("`classify` ended with not_signed_in: No Jev API key was found.", printed)
        self.assertEqual({tuple(call["args"][:1]) for call in stand_in.calls()}, {("find-generic-password",)})
        self.assertEqual(live_check.command(folder, str(stand_in.program), "info")[3:6],
                         [str(folder / "scripts/contract_entry.py"), str(stand_in.program), "1.0"])
        self.assertEqual(live_check.command(folder, None, "info"), [str(folder / "bin/arbol-classifier"), "info"])


if __name__ == "__main__":
    unittest.main()
