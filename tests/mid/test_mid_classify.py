"""Commented mid-tier selections; see MID_TIER.md before restoring a case."""

# Restore the needed imports and class header only for an explicit testing task.
# import test_classify as _support
# from test_classify import (
#     Attempts,
#     Classify,
#     Deadline,
#     Errors,
#     FILE,
#     Failure,
#     FakeJev,
#     Path,
#     REQUEST,
#     Settings,
#     call,
#     classify,
#     failure_of,
#     fixed_key,
#     json,
#     patch,
#     time,
#     unittest,
# )


# class Classify(_support.Classify):
# TEST-TIER-DISABLED-BEGIN tests/test_classify.py::Classify.test_adds_the_key_the_pinned_model_and_the_limits
#     def test_adds_the_key_the_pinned_model_and_the_limits(self) -> None:
#         settings = Settings(model="jev-1.14.0", max_request_bytes=500, endpoint="http://127.0.0.1:8649/v1/systemone")
#         send = FakeJev()
#         result = classify(json.dumps(REQUEST).encode(), settings, FILE, Deadline(4.5), send=send, key=fixed_key)
#         [(endpoint, body, key, timeout)] = send.calls
#         self.assertEqual((endpoint, key, timeout), ("http://127.0.0.1:8649/v1/systemone", "key-marker", 4.5))
#         self.assertEqual(json.loads(body), {**REQUEST, "model": "jev-1.14.0"})
#         self.assertEqual(result, {"model": "jev-1.14.0", "answers": {"work": {"type": "noul", "noul": 0.9}}})
#         with self.assertRaises(Failure) as caught:
#             classify(json.dumps(REQUEST).encode(), Settings(max_request_bytes=len(body) - 1), FILE, Deadline(4.5),
#                      send=send, key=fixed_key)
#         self.assertEqual((caught.exception.code, len(send.calls)), ("invalid_input", 1))
# TEST-TIER-DISABLED-END tests/test_classify.py::Classify.test_adds_the_key_the_pinned_model_and_the_limits

# TEST-TIER-DISABLED-BEGIN tests/test_classify.py::Classify.test_interprets_no_question
#     def test_interprets_no_question(self) -> None:
#         request = {"state": [1, {"a": None}], "questions": {"work": {"type": "rank", "instructions": None, "x": 1}}}
#         send = FakeJev()
#         classify(json.dumps(request).encode(), Settings(), FILE, Deadline(10), send=send, key=fixed_key)
#         self.assertEqual(json.loads(send.calls[0][1]), {**request, "model": "jev-1.13.0"})
# TEST-TIER-DISABLED-END tests/test_classify.py::Classify.test_interprets_no_question

# TEST-TIER-DISABLED-BEGIN tests/test_classify.py::Classify.test_a_refused_request_reads_no_key_and_sends_nothing
#     def test_a_refused_request_reads_no_key_and_sends_nothing(self) -> None:
#         send = FakeJev()
#         keys: list[Settings] = []
#
#         def key(settings: Settings, settings_file: Path, deadline: Deadline) -> str:
#             keys.append(settings)
#             return "key-marker"
#
#         for data in (b"{", json.dumps({**REQUEST, "model": "jev-1.13.0"}).encode(),
#                      json.dumps({**REQUEST, "state": "x" * 64000}).encode()):
#             with self.assertRaises(Failure):
#                 classify(data, Settings(), FILE, Deadline(10), send=send, key=key)
#         self.assertEqual((keys, send.calls), ([], []))
# TEST-TIER-DISABLED-END tests/test_classify.py::Classify.test_a_refused_request_reads_no_key_and_sends_nothing

# TEST-TIER-DISABLED-BEGIN tests/test_classify.py::Classify.test_starts_nothing_but_the_key_command
#     def test_starts_nothing_but_the_key_command(self) -> None:
#         started: list[list[str]] = []
#         original = subprocess.Popen.__init__
#
#         def recording(popen: subprocess.Popen[bytes], args: Any, *rest: Any, **options: Any) -> None:
#             started.append(list(args))
#             original(popen, args, *rest, **options)
#
#         command = (sys.executable, "-I", "-B", "-c", "print('key-marker')")
#         send = FakeJev()
#         with patch.object(subprocess.Popen, "__init__", recording):
#             classify(json.dumps(REQUEST).encode(), Settings(secret_command=command), FILE, Deadline(10), send=send)
#         self.assertEqual(started, [list(command)])
#         self.assertEqual(send.calls[0][2], "key-marker")
# TEST-TIER-DISABLED-END tests/test_classify.py::Classify.test_starts_nothing_but_the_key_command

# TEST-TIER-DISABLED-BEGIN tests/test_classify.py::Classify.test_starts_nothing_but_security_for_the_key_from_the_keychain
#     def test_starts_nothing_but_security_for_the_key_from_the_keychain(self) -> None:
#         security = security_stand_in(self)
#         security.put(SERVICE, ACCOUNT, "key-marker-item")
#         started: list[list[str]] = []
#         original = subprocess.Popen.__init__
#
#         def recording(popen: subprocess.Popen[bytes], args: Any, *rest: Any, **options: Any) -> None:
#             started.append(list(args))
#             original(popen, args, *rest, **options)
#
#         send = FakeJev()
#         with patch.object(subprocess.Popen, "__init__", recording):
#             classify(json.dumps(REQUEST).encode(), Settings(), FILE, Deadline(10), send=send)
#         self.assertEqual(started, [[str(security.program), "find-generic-password", "-s", SERVICE, "-a", ACCOUNT, "-w"]])
#         self.assertEqual(send.calls[0][2], "key-marker-item")
# TEST-TIER-DISABLED-END tests/test_classify.py::Classify.test_starts_nothing_but_security_for_the_key_from_the_keychain



# class Errors(_support.Errors):
# TEST-TIER-DISABLED-BEGIN tests/test_classify.py::Errors.test_statuses_that_no_further_attempt_can_help
#     def test_statuses_that_no_further_attempt_can_help(self) -> None:
#         for status, code in ((401, "credential_rejected"), (422, "invalid_input"), (413, "invalid_input"),
#                              (400, "vendor_error"), (403, "vendor_error"), (404, "vendor_error"), (302, "vendor_error"),
#                              (418, "vendor_error")):
#             with self.subTest(status=status):
#                 send = FakeJev(status, 200)
#                 failure = failure_of(self, send)
#                 self.assertEqual((failure.code, len(send.calls)), (code, 1))
#                 self.assertEqual(failure.error()["detail"], {"basis": "fields", "vendorStatus": status})
#                 self.assertFalse(failure.error()["retryable"])
# TEST-TIER-DISABLED-END tests/test_classify.py::Errors.test_statuses_that_no_further_attempt_can_help

# TEST-TIER-DISABLED-BEGIN tests/test_classify.py::Errors.test_statuses_and_failed_connections_that_are_tried_again
#     def test_statuses_and_failed_connections_that_are_tried_again(self) -> None:
#         unreachable = Failure("vendor_unavailable", "Jev could not be reached at http://127.0.0.1:9/v1/systemone.")
#         for status, code in ((429, "rate_limited"), (529, "vendor_unavailable"), (500, "vendor_unavailable"),
#                              (502, "vendor_unavailable"), (503, "vendor_unavailable"), (599, "vendor_unavailable"),
#                              (unreachable, "vendor_unavailable")):
#             with self.subTest(status=status):
#                 send = FakeJev(status)
#                 failure = failure_of(self, send)
#                 self.assertEqual((failure.code, len(send.calls)), (code, 3))
#                 self.assertTrue(failure.error()["retryable"])
#                 self.assertIn("Attempts made: 3", str(failure))
# TEST-TIER-DISABLED-END tests/test_classify.py::Errors.test_statuses_and_failed_connections_that_are_tried_again

# TEST-TIER-DISABLED-BEGIN tests/test_classify.py::Errors.test_a_further_attempt_that_succeeds
#     def test_a_further_attempt_that_succeeds(self) -> None:
#         unreachable = Failure("vendor_unavailable", "Jev could not be reached.")
#         for statuses in ((529, 200), (429, 500, 200), (unreachable, 200), (unreachable, 429, 200)):
#             with self.subTest(statuses=statuses):
#                 send = FakeJev(*statuses)
#                 self.assertEqual(call(send), {"model": "jev-1.13.0", "answers": {"work": {"type": "noul", "noul": 0.9}}})
#                 self.assertEqual(len(send.calls), len(statuses))
# TEST-TIER-DISABLED-END tests/test_classify.py::Errors.test_a_further_attempt_that_succeeds

# TEST-TIER-DISABLED-BEGIN tests/test_classify.py::Errors.test_a_further_attempt_only_where_it_can_help
#     def test_a_further_attempt_only_where_it_can_help(self) -> None:
#         for statuses, code, attempts in (((529, 401), "credential_rejected", 2), ((429, 422), "invalid_input", 2),
#                                          ((500, 400), "vendor_error", 2)):
#             with self.subTest(statuses=statuses):
#                 send = FakeJev(*statuses)
#                 failure = failure_of(self, send)
#                 self.assertEqual((failure.code, len(send.calls)), (code, attempts))
#         stopped = FakeJev(200, reply={"model": "jev-9.9.9", "answers": {}})
#         self.assertEqual((failure_of(self, stopped).code, len(stopped.calls)), ("vendor_error", 1))
# TEST-TIER-DISABLED-END tests/test_classify.py::Errors.test_a_further_attempt_only_where_it_can_help

# TEST-TIER-DISABLED-BEGIN tests/test_classify.py::Errors.test_rate_limited_names_the_time_jev_named
#     def test_rate_limited_names_the_time_jev_named(self) -> None:
#         failure = failure_of(self, FakeJev(429, retry_after=7))
#         self.assertEqual(failure.error()["retryAfterSeconds"], 7)
#         self.assertNotIn("retryAfterSeconds", failure_of(self, FakeJev(429)).error())
#         self.assertNotIn("retryAfterSeconds", failure_of(self, FakeJev(503, retry_after=7)).error())
# TEST-TIER-DISABLED-END tests/test_classify.py::Errors.test_rate_limited_names_the_time_jev_named

# TEST-TIER-DISABLED-BEGIN tests/test_classify.py::Errors.test_the_message_says_what_jev_said_without_the_judged_text_or_the_key
#     def test_the_message_says_what_jev_said_without_the_judged_text_or_the_key(self) -> None:
#         cases: tuple[tuple[object, str], ...] = (
#             ({"detail": [{"loc": ["body", "questions", "work", "criteria"], "msg": "Field required", "type": "missing",
#                           "input": "judged marker"}]}, "body.questions.work.criteria: Field required"),
#             ({"detail": "Too many tokens in judged marker"}, "Too many tokens in …"),
#             ({"message": "Invalid API key key-marker"}, "Invalid API key …"),
#             ({"error": {"message": "Model jev-1.13.0 is retired", "input": "judged marker"}},
#              "Model jev-1.13.0 is retired"),
#             ({"error": "x" * 400}, "x" * 299 + "…"),
#         )
#         for reply, said in cases:
#             with self.subTest(reply=reply):
#                 failure = failure_of(self, FakeJev(422, reply=reply))
#                 self.assertEqual(str(failure), f"Jev refused the request as invalid: {said}")
#                 self.assertIn(said, str(failure_of(self, FakeJev(401, reply=reply))))
#         failure = failure_of(self, FakeJev(422, reply=["judged marker"]))
#         self.assertEqual(
#             str(failure), "Jev refused the request as invalid (HTTP status 422) and gave no reason that can be shown."
#         )
# TEST-TIER-DISABLED-END tests/test_classify.py::Errors.test_the_message_says_what_jev_said_without_the_judged_text_or_the_key



# class Attempts(_support.Attempts):
# TEST-TIER-DISABLED-BEGIN tests/test_classify.py::Attempts.test_the_waits_between_attempts
#     def test_the_waits_between_attempts(self) -> None:
#         with patch("arbol_classifier.limits.SCALE", 0.1):
#             send = FakeJev(529)
#             failure_of(self, send)
#         first, second, third = send.times
#         self.assertGreaterEqual(second - first, 0.05)
#         self.assertLess(second - first, 0.09)
#         self.assertGreaterEqual(third - second, 0.1)
#         self.assertLess(third - second, 0.14)
# TEST-TIER-DISABLED-END tests/test_classify.py::Attempts.test_the_waits_between_attempts

# TEST-TIER-DISABLED-BEGIN tests/test_classify.py::Attempts.test_a_slow_key_reaches_the_time_limit
#     def test_a_slow_key_reaches_the_time_limit(self) -> None:
#         command = (sys.executable, "-I", "-B", "-c", "import time; time.sleep(5)")
#         send = FakeJev()
#         started = time.monotonic()
#         with patch("arbol_classifier.limits.SCALE", 0.1), self.assertRaises(Failure) as caught:
#             classify(json.dumps(REQUEST).encode(), Settings(secret_command=command), FILE, Deadline(3), send=send)
#         self.assertLess(time.monotonic() - started, 2)
#         self.assertEqual((caught.exception.code, send.calls), ("limit_reached", []))
#         self.assertIn("3 seconds", str(caught.exception))
# TEST-TIER-DISABLED-END tests/test_classify.py::Attempts.test_a_slow_key_reaches_the_time_limit


# Original deferred imports (restore at the required scope, never blindly at the tail).
# TEST-TIER-IMPORTS-BEGIN tests/test_classify.py:5
# import subprocess
# TEST-TIER-IMPORTS-END tests/test_classify.py:5

# TEST-TIER-IMPORTS-BEGIN tests/test_classify.py:6
# import sys
# TEST-TIER-IMPORTS-END tests/test_classify.py:6

# TEST-TIER-IMPORTS-BEGIN tests/test_classify.py:10
# from typing import Any
# TEST-TIER-IMPORTS-END tests/test_classify.py:10

# TEST-TIER-IMPORTS-BEGIN tests/test_classify.py:13
# from stand_ins import security_stand_in
# TEST-TIER-IMPORTS-END tests/test_classify.py:13

# TEST-TIER-IMPORTS-BEGIN tests/test_classify.py:17
# from arbol_classifier.key import ACCOUNT, SERVICE
# TEST-TIER-IMPORTS-END tests/test_classify.py:17

raise RuntimeError("Mid-tier tests require an explicitly requested testing task; see MID_TIER.md.")
