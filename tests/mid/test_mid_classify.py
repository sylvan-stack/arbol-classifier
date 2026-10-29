
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: tests/mid/test_mid_classify.py::Classify.test_adds_the_key_the_pinned_model_and_the_limits
# Reason: Uses configured FakeJev replies or local call recordings for behavior covered by retained process/HTTP retry, redaction and deadline scenarios. Adds no independent boundary evidence; the existing top-tier deadline case stays. Case reviewed: Adds the key the pinned model and the limits.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_classify.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_classify.py::Classify.test_interprets_no_question
# Reason: Uses configured FakeJev replies or local call recordings for behavior covered by retained process/HTTP retry, redaction and deadline scenarios. Adds no independent boundary evidence; the existing top-tier deadline case stays. Case reviewed: Interprets no question.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_classify.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_interprets_no_question(self) -> None:
#         request = {"state": [1, {"a": None}], "questions": {"work": {"type": "rank", "instructions": None, "x": 1}}}
#         send = FakeJev()
#         classify(json.dumps(request).encode(), Settings(), FILE, Deadline(10), send=send, key=fixed_key)
#         self.assertEqual(json.loads(send.calls[0][1]), {**request, "model": "jev-1.13.0"})
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_classify.py::Classify.test_a_refused_request_reads_no_key_and_sends_nothing
# Reason: Uses configured FakeJev replies or local call recordings for behavior covered by retained process/HTTP retry, redaction and deadline scenarios. Adds no independent boundary evidence; the existing top-tier deadline case stays. Case reviewed: A refused request reads no key and sends nothing.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_classify.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_classify.py::Classify.test_starts_nothing_but_the_key_command
# Reason: Uses configured FakeJev replies or local call recordings for behavior covered by retained process/HTTP retry, redaction and deadline scenarios. Adds no independent boundary evidence; the existing top-tier deadline case stays. Case reviewed: Starts nothing but the key command.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_classify.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_classify.py::Classify.test_starts_nothing_but_security_for_the_key_from_the_keychain
# Reason: Uses configured FakeJev replies or local call recordings for behavior covered by retained process/HTTP retry, redaction and deadline scenarios. Adds no independent boundary evidence; the existing top-tier deadline case stays. Case reviewed: Starts nothing but security for the key from the keychain.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_classify.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_classify.py::Errors.test_statuses_that_no_further_attempt_can_help
# Reason: Uses configured FakeJev replies or local call recordings for behavior covered by retained process/HTTP retry, redaction and deadline scenarios. Adds no independent boundary evidence; the existing top-tier deadline case stays. Case reviewed: Statuses that no further attempt can help.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_classify.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_classify.py::Errors.test_statuses_and_failed_connections_that_are_tried_again
# Reason: Uses configured FakeJev replies or local call recordings for behavior covered by retained process/HTTP retry, redaction and deadline scenarios. Adds no independent boundary evidence; the existing top-tier deadline case stays. Case reviewed: Statuses and failed connections that are tried again.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_classify.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_classify.py::Errors.test_a_further_attempt_that_succeeds
# Reason: Uses configured FakeJev replies or local call recordings for behavior covered by retained process/HTTP retry, redaction and deadline scenarios. Adds no independent boundary evidence; the existing top-tier deadline case stays. Case reviewed: A further attempt that succeeds.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_classify.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_further_attempt_that_succeeds(self) -> None:
#         unreachable = Failure("vendor_unavailable", "Jev could not be reached.")
#         for statuses in ((529, 200), (429, 500, 200), (unreachable, 200), (unreachable, 429, 200)):
#             with self.subTest(statuses=statuses):
#                 send = FakeJev(*statuses)
#                 self.assertEqual(call(send), {"model": "jev-1.13.0", "answers": {"work": {"type": "noul", "noul": 0.9}}})
#                 self.assertEqual(len(send.calls), len(statuses))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_classify.py::Errors.test_a_further_attempt_only_where_it_can_help
# Reason: Uses configured FakeJev replies or local call recordings for behavior covered by retained process/HTTP retry, redaction and deadline scenarios. Adds no independent boundary evidence; the existing top-tier deadline case stays. Case reviewed: A further attempt only where it can help.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_classify.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_further_attempt_only_where_it_can_help(self) -> None:
#         for statuses, code, attempts in (((529, 401), "credential_rejected", 2), ((429, 422), "invalid_input", 2),
#                                          ((500, 400), "vendor_error", 2)):
#             with self.subTest(statuses=statuses):
#                 send = FakeJev(*statuses)
#                 failure = failure_of(self, send)
#                 self.assertEqual((failure.code, len(send.calls)), (code, attempts))
#         stopped = FakeJev(200, reply={"model": "jev-9.9.9", "answers": {}})
#         self.assertEqual((failure_of(self, stopped).code, len(stopped.calls)), ("vendor_error", 1))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_classify.py::Errors.test_rate_limited_names_the_time_jev_named
# Reason: Uses configured FakeJev replies or local call recordings for behavior covered by retained process/HTTP retry, redaction and deadline scenarios. Adds no independent boundary evidence; the existing top-tier deadline case stays. Case reviewed: Rate limited names the time jev named.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_classify.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_rate_limited_names_the_time_jev_named(self) -> None:
#         failure = failure_of(self, FakeJev(429, retry_after=7))
#         self.assertEqual(failure.error()["retryAfterSeconds"], 7)
#         self.assertNotIn("retryAfterSeconds", failure_of(self, FakeJev(429)).error())
#         self.assertNotIn("retryAfterSeconds", failure_of(self, FakeJev(503, retry_after=7)).error())
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_classify.py::Errors.test_the_message_says_what_jev_said_without_the_judged_text_or_the_key
# Reason: Uses configured FakeJev replies or local call recordings for behavior covered by retained process/HTTP retry, redaction and deadline scenarios. Adds no independent boundary evidence; the existing top-tier deadline case stays. Case reviewed: The message says what jev said without the judged text or the key.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_classify.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
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
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_classify.py::Attempts.test_the_waits_between_attempts
# Reason: Uses configured FakeJev replies or local call recordings for behavior covered by retained process/HTTP retry, redaction and deadline scenarios. Adds no independent boundary evidence; the existing top-tier deadline case stays. Case reviewed: The waits between attempts.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_classify.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_waits_between_attempts(self) -> None:
#         with patch("arbol_classifier.limits.SCALE", 0.1):
#             send = FakeJev(529)
#             failure_of(self, send)
#         first, second, third = send.times
#         self.assertGreaterEqual(second - first, 0.05)
#         self.assertLess(second - first, 0.09)
#         self.assertGreaterEqual(third - second, 0.1)
#         self.assertLess(third - second, 0.14)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_classify.py::Attempts.test_a_slow_key_reaches_the_time_limit
# Reason: Uses configured FakeJev replies or local call recordings for behavior covered by retained process/HTTP retry, redaction and deadline scenarios. Adds no independent boundary evidence; the existing top-tier deadline case stays. Case reviewed: A slow key reaches the time limit.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_classify.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_slow_key_reaches_the_time_limit(self) -> None:
#         command = (sys.executable, "-I", "-B", "-c", "import time; time.sleep(5)")
#         send = FakeJev()
#         started = time.monotonic()
#         with patch("arbol_classifier.limits.SCALE", 0.1), self.assertRaises(Failure) as caught:
#             classify(json.dumps(REQUEST).encode(), Settings(secret_command=command), FILE, Deadline(3), send=send)
#         self.assertLess(time.monotonic() - started, 2)
#         self.assertEqual((caught.exception.code, send.calls), ("limit_reached", []))
#         self.assertIn("3 seconds", str(caught.exception))
# LOW-TIER-SOURCE-END
# LOW-TIER-END
