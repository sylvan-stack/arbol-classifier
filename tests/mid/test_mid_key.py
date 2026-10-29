
# LOW TIER — DO NOT ENABLE OR RECREATE
# Historical examples only. Read before adding related tests; never execute.
# LOW-TIER-BEGIN: tests/mid/test_mid_key.py::Keychain.test_the_key_is_read_from_the_item_at_each_call
# Reason: Repeats credential reading/storing/refusal behavior represented by the retained PTY-to-storage-to-HTTP lifecycle, missing-key scenario and top-tier stdin-only storage case. Extra fixed values and local error text do not justify another case. Case reviewed: The key is read from the item at each call.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_key.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_key_is_read_from_the_item_at_each_call(self) -> None:
#         self.security.put(SERVICE, ACCOUNT, "key-marker-1")
#         self.assertEqual(read_key(Settings(), FILE, Deadline(10)), "key-marker-1")
#         self.security.put(SERVICE, ACCOUNT, "key-marker-2")
#         self.assertEqual(read_key(Settings(), FILE, Deadline(10)), "key-marker-2")
#         self.assertTrue(key_found(Settings(), FILE, 10))
#         self.assertEqual([call["args"] for call in self.security.calls()], [FIND, FIND, FIND])
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_key.py::Keychain.test_only_the_classifiers_own_item_is_read
# Reason: Repeats credential reading/storing/refusal behavior represented by the retained PTY-to-storage-to-HTTP lifecycle, missing-key scenario and top-tier stdin-only storage case. Extra fixed values and local error text do not justify another case. Case reviewed: Only the classifiers own item is read.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_key.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_only_the_classifiers_own_item_is_read(self) -> None:
#         self.security.put(SERVICE, "other", "key-marker-other")
#         self.security.put("mycel", "jev-api-key", "key-marker-mycel")
#         missing(self, Settings(), str(SERVICE), str(ACCOUNT))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_key.py::Keychain.test_no_item
# Reason: Repeats credential reading/storing/refusal behavior represented by the retained PTY-to-storage-to-HTTP lifecycle, missing-key scenario and top-tier stdin-only storage case. Extra fixed values and local error text do not justify another case. Case reviewed: No item.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_key.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_no_item(self) -> None:
#         failure = missing(self, Settings())
#         self.assertEqual(str(failure), NO_KEY)
#         self.assertEqual(failure.remedy, "Store the key with: arbol-classifier add-key")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_key.py::Keychain.test_an_empty_item
# Reason: Repeats credential reading/storing/refusal behavior represented by the retained PTY-to-storage-to-HTTP lifecycle, missing-key scenario and top-tier stdin-only storage case. Extra fixed values and local error text do not justify another case. Case reviewed: An empty item.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_key.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_an_empty_item(self) -> None:
#         self.security.put(SERVICE, ACCOUNT, "")
#         failure = missing(self, Settings(), "the service com.sylvan-stack.arbol.classifier and the account jev",
#                           "the item is empty")
#         self.assertEqual(failure.remedy, "Store the key with: arbol-classifier add-key")
#         self.security.put(SERVICE, ACCOUNT, "  ")
#         missing(self, Settings(), "the item is empty")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_key.py::Keychain.test_an_item_that_cannot_be_a_key
# Reason: Repeats credential reading/storing/refusal behavior represented by the retained PTY-to-storage-to-HTTP lifecycle, missing-key scenario and top-tier stdin-only storage case. Extra fixed values and local error text do not justify another case. Case reviewed: An item that cannot be a key.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_key.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_an_item_that_cannot_be_a_key(self) -> None:
#         for value in ("key-marker with space", "key-marker\nsecond line", "key-markeré"):
#             self.security.put(SERVICE, ACCOUNT, value)
#             missing(self, Settings(), "cannot be a key")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_key.py::Keychain.test_an_item_that_cannot_be_read
# Reason: Repeats credential reading/storing/refusal behavior represented by the retained PTY-to-storage-to-HTTP lifecycle, missing-key scenario and top-tier stdin-only storage case. Extra fixed values and local error text do not justify another case. Case reviewed: An item that cannot be read.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_key.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_an_item_that_cannot_be_read(self) -> None:
#         self.security.put(SERVICE, ACCOUNT, "key-marker")
#         self.security.fail(51)
#         missing(self, Settings(), "could not be read", "status 51")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_key.py::Keychain.test_security_that_cannot_be_started_or_does_not_answer
# Reason: Repeats credential reading/storing/refusal behavior represented by the retained PTY-to-storage-to-HTTP lifecycle, missing-key scenario and top-tier stdin-only storage case. Extra fixed values and local error text do not justify another case. Case reviewed: Security that cannot be started or does not answer.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_key.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_security_that_cannot_be_started_or_does_not_answer(self) -> None:
#         with tempfile.TemporaryDirectory() as name:
#             with patch.object(key_module, "SECURITY", str(Path(name) / "no-such-program")):
#                 missing(self, Settings(), "could not be started")
#             slow = Path(name) / "security"
#             slow.write_text("#!/bin/sh\nsleep 5\n")
#             slow.chmod(0o755)
#             with patch.object(key_module, "SECURITY", str(slow)):
#                 too_slow(self, Settings(), "while the Jev API key was read from the login Keychain")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_key.py::Keychain.test_a_key_command_in_the_settings_takes_the_place_of_the_item
# Reason: Repeats credential reading/storing/refusal behavior represented by the retained PTY-to-storage-to-HTTP lifecycle, missing-key scenario and top-tier stdin-only storage case. Extra fixed values and local error text do not justify another case. Case reviewed: A key command in the settings takes the place of the item.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_key.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_key_command_in_the_settings_takes_the_place_of_the_item(self) -> None:
#         self.security.put(SERVICE, ACCOUNT, "key-marker-item")
#         self.assertEqual(read_key(command("print('key-marker-command')"), FILE, Deadline(10)), "key-marker-command")
#         self.assertEqual(self.security.calls(), [])
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_key.py::KeyCommand.test_what_the_command_prints_is_the_key
# Reason: Repeats credential reading/storing/refusal behavior represented by the retained PTY-to-storage-to-HTTP lifecycle, missing-key scenario and top-tier stdin-only storage case. Extra fixed values and local error text do not justify another case. Case reviewed: What the command prints is the key.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_key.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_what_the_command_prints_is_the_key(self) -> None:
#         self.assertEqual(read_key(command("print('key-marker-1')"), FILE, Deadline(10)), "key-marker-1")
#         self.assertEqual(read_key(command("print('  key-marker-2\\r\\n')"), FILE, Deadline(10)), "key-marker-2")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_key.py::KeyCommand.test_a_command_that_fails_or_prints_nothing_gives_not_signed_in
# Reason: Repeats credential reading/storing/refusal behavior represented by the retained PTY-to-storage-to-HTTP lifecycle, missing-key scenario and top-tier stdin-only storage case. Extra fixed values and local error text do not justify another case. Case reviewed: A command that fails or prints nothing gives not signed in.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_key.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_command_that_fails_or_prints_nothing_gives_not_signed_in(self) -> None:
#         where = f"the command that the settings file {FILE} names for the key"
#         missing(self, command("import sys; print('key-marker'); sys.exit(3)"), where, "failed")
#         missing(self, command("pass"), where, "printed nothing")
#         missing(self, command("print('   ')"), "printed nothing")
#         missing(self, command("print('key-marker with space')"), "not a key")
#         missing(self, command("print('key-marker\\nsecond line')"), "not a key")
#         too_slow(self, command("import time; time.sleep(5)"), f"while the command that the settings file {FILE} names")
#         with tempfile.TemporaryDirectory() as name:
#             missing(self, Settings(secret_command=(str(Path(name) / "no-such-program"),)), "could not be started")
#         self.assertEqual(self.security.calls(), [])
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_key.py::StoreKey.test_a_key_stored_before_is_replaced
# Reason: Repeats credential reading/storing/refusal behavior represented by the retained PTY-to-storage-to-HTTP lifecycle, missing-key scenario and top-tier stdin-only storage case. Extra fixed values and local error text do not justify another case. Case reviewed: A key stored before is replaced.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_key.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_key_stored_before_is_replaced(self) -> None:
#         self.security.put(SERVICE, ACCOUNT, "key-marker-old")
#         self.assertTrue(store_key("key-marker-second"))
#         self.assertEqual(self.security.value(SERVICE, ACCOUNT), "key-marker-second")
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_key.py::StoreKey.test_every_visible_character_reaches_the_item_unchanged
# Reason: Repeats credential reading/storing/refusal behavior represented by the retained PTY-to-storage-to-HTTP lifecycle, missing-key scenario and top-tier stdin-only storage case. Extra fixed values and local error text do not justify another case. Case reviewed: Every visible character reaches the item unchanged.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_key.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_every_visible_character_reaches_the_item_unchanged(self) -> None:
#         for key in ('key"marker\\with\\"quotes', "key'marker$`!#;%&*(){}[]<>|~^?=+,.:@", "-w", '\\"'):
#             store_key(key)
#             self.assertEqual(self.security.value(SERVICE, ACCOUNT), key)
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_key.py::StoreKey.test_only_a_key_that_can_be_one_is_stored
# Reason: Repeats credential reading/storing/refusal behavior represented by the retained PTY-to-storage-to-HTTP lifecycle, missing-key scenario and top-tier stdin-only storage case. Extra fixed values and local error text do not justify another case. Case reviewed: Only a key that can be one is stored.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_key.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_only_a_key_that_can_be_one_is_stored(self) -> None:
#         for key in ("", "key-marker with space", "key-marker\nadd-generic-password -s x -a y -w z"):
#             with self.assertRaises(ValueError):
#                 store_key(key)
#         self.assertEqual(self.security.calls(), [])
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_key.py::StoreKey.test_a_keychain_that_does_not_store_the_key_ends_with_internal
# Reason: Repeats credential reading/storing/refusal behavior represented by the retained PTY-to-storage-to-HTTP lifecycle, missing-key scenario and top-tier stdin-only storage case. Extra fixed values and local error text do not justify another case. Case reviewed: A keychain that does not store the key ends with internal.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_key.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_a_keychain_that_does_not_store_the_key_ends_with_internal(self) -> None:
#         self.security.fail(51)
#         with self.assertRaises(Failure) as caught:
#             store_key("key-marker")
#         self.assertEqual(caught.exception.code, "internal")
#         self.assertIn("could not be stored", str(caught.exception))
#         self.assertNotIn("key-marker", str(caught.exception))
# LOW-TIER-SOURCE-END
# LOW-TIER-END

# LOW-TIER-BEGIN: tests/mid/test_mid_key.py::StoreKey.test_the_item_is_never_removed
# Reason: Repeats credential reading/storing/refusal behavior represented by the retained PTY-to-storage-to-HTTP lifecycle, missing-key scenario and top-tier stdin-only storage case. Extra fixed values and local error text do not justify another case. Case reviewed: The item is never removed.
# Source: arbol-classifier@d625176f8423cd3584f87c99ab19ebde0f5ae077:tests/mid/test_mid_key.py
# Historical fixtures and class context are available at the source revision; no active dependencies restored.
# LOW-TIER-SOURCE-BEGIN
#     def test_the_item_is_never_removed(self) -> None:
#         self.security.put(SERVICE, ACCOUNT, "key-marker-old")
#         store_key("key-marker-new")
#         read_key(Settings(), FILE, Deadline(10))
#         missing(self, command("pass"))
#         commands = [call["args"][0] for call in self.security.calls()] + [
#             word for call in self.security.calls() for word in call["stdin"].split()
#         ]
#         self.assertNotIn("delete-generic-password", commands)
# LOW-TIER-SOURCE-END
# LOW-TIER-END
