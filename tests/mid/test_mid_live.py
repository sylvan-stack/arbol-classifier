"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_live as _support
from test_live import (
    Any,
    INFO,
    Judge,
    Live,
    LiveTest,
    NO_KEY,
    PRETEND,
    Path,
    PretendBuild,
    REPLY,
    ROOT,
    SET_BY_THE_SYSTEM,
    SecurityStandIn,
    WithoutAKey,
    contextlib,
    io,
    json,
    live_check,
    os,
    patch,
    shlex,
    sys,
    tempfile,
    unittest,
)


class Judge(_support.Judge):
# TEST-TIER-BEGIN tests/test_live.py::Judge.test_a_reply_from_another_model_fails
    def test_a_reply_from_another_model_fails(self) -> None:
        with self.assertRaisesRegex(live_check.LiveFailure, "jev-1.14.0"):
            live_check.judge(INFO, {**REPLY, "model": "jev-1.14.0"})
# TEST-TIER-END tests/test_live.py::Judge.test_a_reply_from_another_model_fails

# TEST-TIER-BEGIN tests/test_live.py::Judge.test_a_reply_without_the_answer_fails
    def test_a_reply_without_the_answer_fails(self) -> None:
        kind = REPLY["answers"]["kind"]
        for answers in ({}, {"kind": kind, "extra": kind}, {"kind": {**kind, "choice": "maybe"}},
                        {"kind": {**kind, "type": "noul"}}, {"kind": {**kind, "confidence": 1.5}},
                        {"kind": {**kind, "confidence": True}}):
            with self.subTest(answers=answers), self.assertRaises(live_check.LiveFailure):
                live_check.judge(INFO, {**REPLY, "answers": answers})
# TEST-TIER-END tests/test_live.py::Judge.test_a_reply_without_the_answer_fails

# TEST-TIER-BEGIN tests/test_live.py::Judge.test_a_reply_without_usage_still_holds_the_answer
    def test_a_reply_without_usage_still_holds_the_answer(self) -> None:
        reply = {key: value for key, value in REPLY.items() if key != "usage"}
        self.assertIn("Jev reported no usage", live_check.judge(INFO, reply))
# TEST-TIER-END tests/test_live.py::Judge.test_a_reply_without_usage_still_holds_the_answer



class Live(_support.Live):
# TEST-TIER-BEGIN tests/test_live.py::Live.test_one_choice_question_through_the_builds_own_program
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
# TEST-TIER-END tests/test_live.py::Live.test_one_choice_question_through_the_builds_own_program

# TEST-TIER-BEGIN tests/test_live.py::Live.test_the_program_gets_the_persons_home_and_nothing_else_of_the_environment
    def test_the_program_gets_the_persons_home_and_nothing_else_of_the_environment(self) -> None:
        build = self.build({"info": (0, INFO), "classify": (0, REPLY)})
        with patch.dict(os.environ, {"ARBOL_BUILD_DIR": str(build.folder), "SOMETHING_ELSE": "1"}):
            self.live(build.folder)
        for call in build.calls():
            environment = {name: value for name, value in call["env"].items() if name not in SET_BY_THE_SYSTEM}
            self.assertEqual(environment, live_check.environment())
            self.assertEqual(Path(call["cwd"]).resolve(), self.home.resolve())
# TEST-TIER-END tests/test_live.py::Live.test_the_program_gets_the_persons_home_and_nothing_else_of_the_environment

# TEST-TIER-BEGIN tests/test_live.py::Live.test_without_a_key_it_fails_and_shows_the_programs_refusal
    def test_without_a_key_it_fails_and_shows_the_programs_refusal(self) -> None:
        build = self.build({"info": (0, {**INFO, "keyFound": False}), "classify": (1, NO_KEY)})
        status, printed = self.live(build.folder)
        self.assertEqual(status, 1)
        self.assertIn("live: failed. `classify` ended with not_signed_in: No Jev API key was found.", printed)
        self.assertIn("Remedy: Store the key with: arbol-classifier add-key", printed)
# TEST-TIER-END tests/test_live.py::Live.test_without_a_key_it_fails_and_shows_the_programs_refusal

# TEST-TIER-BEGIN tests/test_live.py::Live.test_a_stand_in_for_jev_cannot_pass
    def test_a_stand_in_for_jev_cannot_pass(self) -> None:
        build = self.build({"info": (0, {**INFO, "endpoint": "http://127.0.0.1:8080/v1/systemone"}),
                            "classify": (0, REPLY)})
        status, printed = self.live(build.folder)
        self.assertEqual(status, 1)
        self.assertIn("the live check asks Jev itself", printed)
        self.assertEqual([call["args"] for call in build.calls()], [["info"]])
# TEST-TIER-END tests/test_live.py::Live.test_a_stand_in_for_jev_cannot_pass

# TEST-TIER-BEGIN tests/test_live.py::Live.test_a_reply_that_is_not_one_json_object_fails
    def test_a_reply_that_is_not_one_json_object_fails(self) -> None:
        build = self.build({"info": (0, INFO), "classify": (0, [])})  # type: ignore[dict-item]
        status, printed = self.live(build.folder)
        self.assertEqual(status, 1)
        self.assertIn("did not print a JSON object", printed)
# TEST-TIER-END tests/test_live.py::Live.test_a_reply_that_is_not_one_json_object_fails

# TEST-TIER-BEGIN tests/test_live.py::Live.test_the_switch_must_name_an_executable_by_its_absolute_path
    def test_the_switch_must_name_an_executable_by_its_absolute_path(self) -> None:
        build = self.build({"info": (0, INFO), "classify": (0, REPLY)})
        for value in ("security", str(self.work / "missing")):
            with self.subTest(value=value), patch.dict(os.environ, {live_check.SECURITY_SWITCH: value}):
                status, printed = self.live(build.folder)
                self.assertEqual(status, 1)
                self.assertIn("absolute path", printed)
        self.assertEqual(build.calls(), [])
# TEST-TIER-END tests/test_live.py::Live.test_the_switch_must_name_an_executable_by_its_absolute_path



class WithoutAKey(_support.WithoutAKey):
# TEST-TIER-BEGIN tests/test_live.py::WithoutAKey.test_a_build_made_while_no_key_is_stored_fails_the_live_check
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
# TEST-TIER-END tests/test_live.py::WithoutAKey.test_a_build_made_while_no_key_is_stored_fails_the_live_check
