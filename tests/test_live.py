# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from stand_ins import SecurityStandIn

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

    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


class Live(LiveTest):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


class WithoutAKey(LiveTest):
    """The real program, started as the live check starts it, with the stand-in for `security` holding no item."""


# Archived complete imports; restore needed names in their original scope, not at this file tail.

# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: tests/test_live.py::Judge.test_the_reply_names_the_model_of_info_and_holds_the_answer
# Reason: Repeats the same valid INFO/REPLY judgement already run by the complete private-program live-check case.
# Source: arbol-classifier@1dfee903bbb88a6f8d95da33ed5a80e507de21f0:tests/test_live.py
# Retained evidence at review: Live.test_one_choice_question_through_the_builds_own_program invokes judge and checks success and usage; invalid/missing answers remain independently tested.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_reply_names_the_model_of_info_and_holds_the_answer(self) -> None:
#         said = live_check.judge(INFO, REPLY)
#         self.assertIn("jev-1.13.0", said)
#         self.assertIn("'request'", said)
#         self.assertIn("333 of input, 38 of output", said)
# LOW-TIER-SOURCE-END
# LOW-TIER-END
