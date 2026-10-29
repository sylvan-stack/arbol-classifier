
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: tests/test_settings.py::SettingsFile.test_the_file_lies_in_the_arbol_folder
# Reason: Copies a literal Path concatenation; it exercises no selection, parsing or failure behavior.
# Source: arbol-classifier@6c6cd54bc1e9f1d721fb034dd3f337c1201c065b:tests/test_settings.py
# Retained evidence at review: Invocation.test_info_reports_identity_settings_and_no_key exercises the settings path through the public CLI.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_file_lies_in_the_arbol_folder(self) -> None:
#         self.assertEqual(settings_path("/Users/someone"), Path("/Users/someone/.arbol/arbol-classifier.json"))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/test_settings.py::SettingsFile.test_a_missing_file_gives_the_defaults
# Reason: Repeats the default dataclass values and the same missing-settings success already exercised by the CLI.
# Source: arbol-classifier@6c6cd54bc1e9f1d721fb034dd3f337c1201c065b:tests/test_settings.py
# Retained evidence at review: Invocation.test_info_reports_identity_settings_and_no_key; settings-file CLI selection and malformed-settings cases remain.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_missing_file_gives_the_defaults(self) -> None:
#         settings = read_settings(self.file)
#         self.assertEqual(settings, Settings())
#         self.assertEqual(
#             (settings.model, settings.timeout_seconds, settings.max_request_bytes, settings.endpoint),
#             ("jev-1.13.0", 10.0, 64000, "https://api.typesafe.ai/v1/systemone"),
#         )
#         self.assertIsNone(settings.secret_command)
#         self.assertEqual(self.read({}), Settings())
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/test_settings.py::SettingsFile.test_every_field_is_read
# Reason: Copies all ordinary settings fields into a dataclass expectation and repeats trivial defaults.
# Source: arbol-classifier@6c6cd54bc1e9f1d721fb034dd3f337c1201c065b:tests/test_settings.py
# Retained evidence at review: Settings-file CLI dispatch, invalid types, Unicode/version boundaries and credential-source behavior remain.
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_every_field_is_read(self) -> None:
#         settings = self.read(
#             {
#                 "model": "jev-2.10.3",
#                 "timeoutSeconds": 2.5,
#                 "maxRequestBytes": 1000,
#                 "endpoint": "http://127.0.0.1:8649/v1/systemone",
#                 "secret": {"from": "command", "command": ["/usr/bin/printf", "key"]},
#             }
#         )
#         self.assertEqual(
#             settings, Settings("jev-2.10.3", 2.5, 1000, "http://127.0.0.1:8649/v1/systemone", ("/usr/bin/printf", "key"))
#         )
#         self.assertEqual(self.read({"timeoutSeconds": 60}).timeout_seconds, 60.0)
#         self.assertIsNone(self.read({"secret": {"from": "keychain"}}).secret_command)
# LOW-TIER-SOURCE-END
# LOW-TIER-END
