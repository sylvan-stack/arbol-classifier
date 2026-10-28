# Test inventory: arbol-classifier

Reviewed source revision: `407a70294b8c3355cf7422f5b6b7abaf95bc7419`. Static inventory dated 28 October 2026. See [TESTS.md](../TESTS.md) for execution and restoration rules.

**Top** means individually reviewed and active. **Mid*** means commented and provisionally reserved for a separate testing task; usefulness still needs assessment before restoration. **Low** means removed in the preceding pruning review. A function/program count is not an assertion count or a discovery result.

## scripts/check_build.py

| Test or check | Tier / state | Justification |
| --- | --- | --- |
| [`unit`](../scripts/check_build.py#L58) | Mid* / refuses | Broad qualification or diagnostic entry point. Its original implementation is commented and the callable refuses, so disabled checks cannot yield a passing release claim. |
| [`contract`](../scripts/check_build.py#L72) | Mid* / refuses | Broad qualification or diagnostic entry point. Its original implementation is commented and the callable refuses, so disabled checks cannot yield a passing release claim. |
| [`live`](../scripts/check_build.py#L83) | Mid* / refuses | Broad qualification or diagnostic entry point. Its original implementation is commented and the callable refuses, so disabled checks cannot yield a passing release claim. |

## scripts/contract_checks.py

| Test or check | Tier / state | Justification |
| --- | --- | --- |
| [`info.identity`](../scripts/contract_checks.py#L274) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`info.defaults`](../scripts/contract_checks.py#L289) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`info.settings-file`](../scripts/contract_checks.py#L303) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`info.settings-option`](../scripts/contract_checks.py#L318) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`info.accepted-settings`](../scripts/contract_checks.py#L338) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`settings.faulty-file`](../scripts/contract_checks.py#L358) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`settings.unknown-key`](../scripts/contract_checks.py#L374) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`settings.moving-model`](../scripts/contract_checks.py#L389) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`settings.faulty-fields`](../scripts/contract_checks.py#L401) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`cli.no-command`](../scripts/contract_checks.py#L442) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`cli.unknown-command`](../scripts/contract_checks.py#L453) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`cli.unknown-option`](../scripts/contract_checks.py#L464) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`cli.build-selector`](../scripts/contract_checks.py#L476) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`cli.extra-argument`](../scripts/contract_checks.py#L487) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`cli.option-once`](../scripts/contract_checks.py#L498) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`cli.option-value`](../scripts/contract_checks.py#L509) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`cli.timeout`](../scripts/contract_checks.py#L522) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`classify.choice`](../scripts/contract_checks.py#L551) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`classify.noul`](../scripts/contract_checks.py#L569) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`classify.score`](../scripts/contract_checks.py#L588) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`classify.what-is-sent`](../scripts/contract_checks.py#L606) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`classify.pinned-model`](../scripts/contract_checks.py#L631) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`classify.other-model`](../scripts/contract_checks.py#L647) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`classify.missing-answer`](../scripts/contract_checks.py#L668) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`classify.names-a-model`](../scripts/contract_checks.py#L696) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`classify.size-limit`](../scripts/contract_checks.py#L710) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`classify.malformed`](../scripts/contract_checks.py#L734) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`classify.passes-questions-through`](../scripts/contract_checks.py#L758) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`classify.endpoint-elsewhere`](../scripts/contract_checks.py#L775) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`classify.writes-nothing`](../scripts/contract_checks.py#L793) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`key.keychain`](../scripts/contract_checks.py#L828) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`key.not-found`](../scripts/contract_checks.py#L852) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`key.only-in-the-bearer-token`](../scripts/contract_checks.py#L887) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`add-key.at-a-terminal`](../scripts/contract_checks.py#L916) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`add-key.no-terminal`](../scripts/contract_checks.py#L949) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`add-key.not-a-key`](../scripts/contract_checks.py#L963) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`add-key.keychain-refuses`](../scripts/contract_checks.py#L978) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`cli.add-key-arguments`](../scripts/contract_checks.py#L991) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`cli.build-entry`](../scripts/contract_checks.py#L1003) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`errors.credential-rejected`](../scripts/contract_checks.py#L1046) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`errors.invalid-at-jev`](../scripts/contract_checks.py#L1061) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`errors.rate-limited`](../scripts/contract_checks.py#L1085) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`errors.vendor-unavailable`](../scripts/contract_checks.py#L1103) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`errors.vendor-error`](../scripts/contract_checks.py#L1132) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`attempts.until-an-answer`](../scripts/contract_checks.py#L1150) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`attempts.waits`](../scripts/contract_checks.py#L1172) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`limits.no-wait-past-the-limit`](../scripts/contract_checks.py#L1188) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`limits.time-limit`](../scripts/contract_checks.py#L1205) | Mid* / commented | Contract scenario with a multi-step fixture and compatibility assertions. Reserved for explicit qualification; this reset does not establish a reason to keep the whole scenario active. |
| [`run_contract`](../scripts/contract_checks.py#L1275) | Mid* / refuses | Broad qualification or diagnostic entry point. Its original implementation is commented and the callable refuses, so disabled checks cannot yield a passing release claim. |

## scripts/live_check.py

| Test or check | Tier / state | Justification |
| --- | --- | --- |
| [`run_live`](../scripts/live_check.py#L113) | Mid* / refuses | Broad qualification or diagnostic entry point. Its original implementation is commented and the callable refuses, so disabled checks cannot yield a passing release claim. |

## tests/test_arguments.py

| Test or check | Tier / state | Justification |
| --- | --- | --- |
| [`Arguments.test_timeout_takes_one_to_sixty_seconds`](../tests/test_arguments.py#L17) | Mid* / commented | Scenario: timeout takes one to sixty seconds. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Arguments.test_missing_and_unknown_commands`](../tests/test_arguments.py#L29) | Mid* / commented | Scenario: missing and unknown commands. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Arguments.test_unknown_options_and_build_selection`](../tests/test_arguments.py#L39) | Mid* / commented | Scenario: unknown options and build selection. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Arguments.test_option_values_are_required_and_given_once`](../tests/test_arguments.py#L54) | Mid* / commented | Scenario: option values are required and given once. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |

## tests/test_classify.py

| Test or check | Tier / state | Justification |
| --- | --- | --- |
| [`Classify.test_adds_the_key_the_pinned_model_and_the_limits`](../tests/test_classify.py#L59) | Mid* / commented | Scenario: adds the key the pinned model and the limits. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Classify.test_interprets_no_question`](../tests/test_classify.py#L74) | Mid* / commented | Scenario: interprets no question. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Classify.test_a_refused_request_reads_no_key_and_sends_nothing`](../tests/test_classify.py#L82) | Mid* / commented | Scenario: a refused request reads no key and sends nothing. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Classify.test_starts_nothing_but_the_key_command`](../tests/test_classify.py#L98) | Mid* / commented | Scenario: starts nothing but the key command. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Classify.test_starts_nothing_but_security_for_the_key_from_the_keychain`](../tests/test_classify.py#L115) | Mid* / commented | Scenario: starts nothing but security for the key from the keychain. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Errors.test_statuses_that_no_further_attempt_can_help`](../tests/test_classify.py#L142) | Mid* / commented | Scenario: statuses that no further attempt can help. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Errors.test_statuses_and_failed_connections_that_are_tried_again`](../tests/test_classify.py#L155) | Mid* / commented | Scenario: statuses and failed connections that are tried again. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Errors.test_a_further_attempt_that_succeeds`](../tests/test_classify.py#L169) | Mid* / commented | Scenario: a further attempt that succeeds. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Errors.test_a_further_attempt_only_where_it_can_help`](../tests/test_classify.py#L179) | Mid* / commented | Scenario: a further attempt only where it can help. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Errors.test_rate_limited_names_the_time_jev_named`](../tests/test_classify.py#L191) | Mid* / commented | Scenario: rate limited names the time jev named. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Errors.test_the_message_says_what_jev_said_without_the_judged_text_or_the_key`](../tests/test_classify.py#L199) | Mid* / commented | Scenario: the message says what jev said without the judged text or the key. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Attempts.test_the_waits_between_attempts`](../tests/test_classify.py#L225) | Mid* / commented | Scenario: the waits between attempts. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Attempts.test_no_wait_goes_past_the_time_limit`](../tests/test_classify.py#L237) | Top / active | Puts the deadline between the first and second retry waits. Checks that the call returns the last vendor refusal after two sends instead of sleeping or retrying past the total budget. |
| [`Attempts.test_a_slow_key_reaches_the_time_limit`](../tests/test_classify.py#L247) | Mid* / commented | Scenario: a slow key reaches the time limit. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |

## tests/test_cli.py

| Test or check | Tier / state | Justification |
| --- | --- | --- |
| [`Invocation.test_info_reports_identity_settings_and_no_key`](../tests/test_cli.py#L20) | Mid* / commented | Scenario: info reports identity settings and no key. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Invocation.test_info_says_whether_a_key_was_found_never_the_key`](../tests/test_cli.py#L40) | Mid* / commented | Scenario: info says whether a key was found never the key. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Invocation.test_add_key_stores_what_was_typed`](../tests/test_cli.py#L51) | Mid* / commented | Scenario: add key stores what was typed. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Invocation.test_add_key_refuses_what_cannot_be_a_key`](../tests/test_cli.py#L65) | Mid* / commented | Scenario: add key refuses what cannot be a key. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Invocation.test_add_key_takes_no_options_and_no_arguments`](../tests/test_cli.py#L82) | Mid* / commented | Scenario: add key takes no options and no arguments. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Invocation.test_info_reads_the_named_settings_file`](../tests/test_cli.py#L94) | Mid* / commented | Scenario: info reads the named settings file. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Invocation.test_refusals_are_error_objects`](../tests/test_cli.py#L107) | Mid* / commented | Scenario: refusals are error objects. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Invocation.test_classify_reads_the_request_on_standard_input`](../tests/test_cli.py#L122) | Mid* / commented | Scenario: classify reads the request on standard input. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Invocation.test_standard_input_is_read_until_it_ends_or_the_time_limit`](../tests/test_cli.py#L146) | Mid* / commented | Scenario: standard input is read until it ends or the time limit. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Invocation.test_only_classify_reads_standard_input`](../tests/test_cli.py#L169) | Mid* / commented | Scenario: only classify reads standard input. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Invocation.test_a_refused_request_is_an_error_object`](../tests/test_cli.py#L178) | Mid* / commented | Scenario: a refused request is an error object. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Invocation.test_an_unexpected_defect_is_internal`](../tests/test_cli.py#L190) | Mid* / commented | Scenario: an unexpected defect is internal. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Invocation.test_the_program_prints_one_json_document`](../tests/test_cli.py#L201) | Mid* / commented | Scenario: the program prints one json document. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |

## tests/test_identity.py

| Test or check | Tier / state | Justification |
| --- | --- | --- |
| [`Identity.test_a_damaged_record_is_a_defect`](../tests/test_identity.py#L33) | Mid* / commented | Scenario: a damaged record is a defect. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Identity.test_another_package_is_not_this_one`](../tests/test_identity.py#L54) | Mid* / commented | Scenario: another package is not this one. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |

## tests/test_jev.py

| Test or check | Tier / state | Justification |
| --- | --- | --- |
| [`Transport.test_the_body_goes_to_the_endpoint_with_the_key_as_a_bearer_token`](../tests/test_jev.py#L71) | Mid* / commented | Scenario: the body goes to the endpoint with the key as a bearer token. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Transport.test_an_address_on_this_mac`](../tests/test_jev.py#L90) | Mid* / commented | Scenario: an address on this mac. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Transport.test_an_endpoint_on_this_mac_that_leads_elsewhere_is_refused_before_anything_is_sent`](../tests/test_jev.py#L106) | Mid* / commented | Scenario: an endpoint on this mac that leads elsewhere is refused before anything is sent. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Transport.test_on_this_mac`](../tests/test_jev.py#L121) | Mid* / commented | Scenario: on this mac. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Transport.test_an_attempt_that_cannot_be_made`](../tests/test_jev.py#L129) | Mid* / commented | Scenario: an attempt that cannot be made. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Transport.test_an_attempt_ends_with_the_time_limit_of_the_call`](../tests/test_jev.py#L146) | Mid* / commented | Scenario: an attempt ends with the time limit of the call. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Transport.test_retry_after_in_seconds`](../tests/test_jev.py#L157) | Mid* / commented | Scenario: retry after in seconds. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |

## tests/test_key.py

| Test or check | Tier / state | Justification |
| --- | --- | --- |
| [`Keychain.test_the_key_is_read_from_the_item_at_each_call`](../tests/test_key.py#L60) | Mid* / commented | Scenario: the key is read from the item at each call. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Keychain.test_only_the_classifiers_own_item_is_read`](../tests/test_key.py#L70) | Mid* / commented | Scenario: only the classifiers own item is read. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Keychain.test_no_item`](../tests/test_key.py#L77) | Mid* / commented | Scenario: no item. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Keychain.test_an_empty_item`](../tests/test_key.py#L84) | Mid* / commented | Scenario: an empty item. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Keychain.test_an_item_that_cannot_be_a_key`](../tests/test_key.py#L94) | Mid* / commented | Scenario: an item that cannot be a key. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Keychain.test_an_item_that_cannot_be_read`](../tests/test_key.py#L101) | Mid* / commented | Scenario: an item that cannot be read. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Keychain.test_security_that_cannot_be_started_or_does_not_answer`](../tests/test_key.py#L108) | Mid* / commented | Scenario: security that cannot be started or does not answer. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Keychain.test_a_key_command_in_the_settings_takes_the_place_of_the_item`](../tests/test_key.py#L120) | Mid* / commented | Scenario: a key command in the settings takes the place of the item. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`KeyCommand.test_what_the_command_prints_is_the_key`](../tests/test_key.py#L132) | Mid* / commented | Scenario: what the command prints is the key. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`KeyCommand.test_a_command_that_fails_or_prints_nothing_gives_not_signed_in`](../tests/test_key.py#L138) | Mid* / commented | Scenario: a command that fails or prints nothing gives not signed in. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`StoreKey.test_the_key_goes_to_security_on_standard_input_never_as_an_argument`](../tests/test_key.py#L157) | Top / active | Records the security subprocess boundary and verifies the stored key through a later read. Detects credential exposure through process arguments or environment while still proving that storage worked. |
| [`StoreKey.test_a_key_stored_before_is_replaced`](../tests/test_key.py#L169) | Mid* / commented | Scenario: a key stored before is replaced. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`StoreKey.test_every_visible_character_reaches_the_item_unchanged`](../tests/test_key.py#L176) | Mid* / commented | Scenario: every visible character reaches the item unchanged. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`StoreKey.test_only_a_key_that_can_be_one_is_stored`](../tests/test_key.py#L183) | Mid* / commented | Scenario: only a key that can be one is stored. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`StoreKey.test_a_keychain_that_does_not_store_the_key_ends_with_internal`](../tests/test_key.py#L191) | Mid* / commented | Scenario: a keychain that does not store the key ends with internal. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`StoreKey.test_the_item_is_never_removed`](../tests/test_key.py#L201) | Mid* / commented | Scenario: the item is never removed. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |

## tests/test_live.py

| Test or check | Tier / state | Justification |
| --- | --- | --- |
| [`Judge.test_a_reply_from_another_model_fails`](../tests/test_live.py#L97) | Mid* / commented | Scenario: a reply from another model fails. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Judge.test_a_reply_without_the_answer_fails`](../tests/test_live.py#L103) | Mid* / commented | Scenario: a reply without the answer fails. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Judge.test_a_reply_without_usage_still_holds_the_answer`](../tests/test_live.py#L113) | Mid* / commented | Scenario: a reply without usage still holds the answer. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Live.test_one_choice_question_through_the_builds_own_program`](../tests/test_live.py#L122) | Mid* / commented | Scenario: one choice question through the builds own program. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Live.test_the_program_gets_the_persons_home_and_nothing_else_of_the_environment`](../tests/test_live.py#L135) | Mid* / commented | Scenario: the program gets the persons home and nothing else of the environment. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Live.test_without_a_key_it_fails_and_shows_the_programs_refusal`](../tests/test_live.py#L146) | Mid* / commented | Scenario: without a key it fails and shows the programs refusal. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Live.test_a_stand_in_for_jev_cannot_pass`](../tests/test_live.py#L155) | Mid* / commented | Scenario: a stand in for jev cannot pass. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Live.test_a_reply_that_is_not_one_json_object_fails`](../tests/test_live.py#L165) | Mid* / commented | Scenario: a reply that is not one json object fails. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Live.test_the_switch_must_name_an_executable_by_its_absolute_path`](../tests/test_live.py#L173) | Mid* / commented | Scenario: the switch must name an executable by its absolute path. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`WithoutAKey.test_a_build_made_while_no_key_is_stored_fails_the_live_check`](../tests/test_live.py#L188) | Mid* / commented | Scenario: a build made while no key is stored fails the live check. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |

## tests/test_packaging.py

| Test or check | Tier / state | Justification |
| --- | --- | --- |
| [`Packaging.test_corrupted_cached_distribution_is_refused_without_a_download`](../tests/test_packaging.py#L16) | Mid* / commented | Scenario: corrupted cached distribution is refused without a download. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Packaging.test_archive_pin_rejects_nonhex_digests_and_untrusted_sources`](../tests/test_packaging.py#L35) | Mid* / commented | Scenario: archive pin rejects nonhex digests and untrusted sources. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Packaging.test_candidate_cannot_overwrite_a_numbered_build`](../tests/test_packaging.py#L48) | Mid* / commented | Scenario: candidate cannot overwrite a numbered build. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Packaging.test_build_record_requires_matching_number_entry_and_version`](../tests/test_packaging.py#L56) | Mid* / commented | Scenario: build record requires matching number entry and version. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |

## tests/test_reply.py

| Test or check | Tier / state | Justification |
| --- | --- | --- |
| [`Replies.test_the_reply_is_given_as_jev_gave_it`](../tests/test_reply.py#L23) | Mid* / commented | Scenario: the reply is given as jev gave it. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Replies.test_a_reply_from_another_model_fails`](../tests/test_reply.py#L34) | Mid* / commented | Scenario: a reply from another model fails. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Replies.test_every_question_asked_has_an_answer_and_no_other_has`](../tests/test_reply.py#L44) | Mid* / commented | Scenario: every question asked has an answer and no other has. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Replies.test_a_reply_that_is_not_json_fails`](../tests/test_reply.py#L55) | Mid* / commented | Scenario: a reply that is not json fails. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |

## tests/test_request.py

| Test or check | Tier / state | Justification |
| --- | --- | --- |
| [`Requests.test_no_question_is_interpreted`](../tests/test_request.py#L27) | Mid* / commented | Scenario: no question is interpreted. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Requests.test_only_the_listed_checks`](../tests/test_request.py#L42) | Mid* / commented | Scenario: only the listed checks. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Requests.test_a_request_that_names_a_model_is_refused`](../tests/test_request.py#L62) | Mid* / commented | Scenario: a request that names a model is refused. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Requests.test_the_judged_text_is_in_no_message`](../tests/test_request.py#L69) | Mid* / commented | Scenario: the judged text is in no message. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`SizeLimit.test_the_limit_is_measured_on_the_body_as_it_is_sent`](../tests/test_request.py#L80) | Mid* / commented | Scenario: the limit is measured on the body as it is sent. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`SizeLimit.test_text_is_counted_in_bytes_of_utf_8`](../tests/test_request.py#L94) | Mid* / commented | Scenario: text is counted in bytes of utf 8. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`SizeLimit.test_nothing_is_cut`](../tests/test_request.py#L101) | Mid* / commented | Scenario: nothing is cut. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`SizeLimit.test_a_body_that_cannot_be_sent_is_refused`](../tests/test_request.py#L112) | Mid* / commented | Scenario: a body that cannot be sent is refused. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |

## tests/test_settings.py

| Test or check | Tier / state | Justification |
| --- | --- | --- |
| [`SettingsFile.test_a_file_that_cannot_be_read_as_settings`](../tests/test_settings.py#L38) | Mid* / commented | Scenario: a file that cannot be read as settings. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`SettingsFile.test_an_unknown_key_refuses_the_file`](../tests/test_settings.py#L53) | Mid* / commented | Scenario: an unknown key refuses the file. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`SettingsFile.test_a_name_that_moves_is_refused_as_model`](../tests/test_settings.py#L62) | Mid* / commented | Scenario: a name that moves is refused as model. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`SettingsFile.test_faulty_fields_are_named_without_their_values`](../tests/test_settings.py#L70) | Mid* / commented | Scenario: faulty fields are named without their values. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Addresses.test_exact_versions`](../tests/test_settings.py#L103) | Mid* / commented | Scenario: exact versions. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Addresses.test_only_jev_or_this_mac`](../tests/test_settings.py#L111) | Mid* / commented | Scenario: only jev or this mac. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |

## tests/test_terminal.py

| Test or check | Tier / state | Justification |
| --- | --- | --- |
| [`Terminal.test_the_key_is_read_with_echo_off_and_the_terminal_is_set_back`](../tests/test_terminal.py#L26) | Mid* / commented | Scenario: the key is read with echo off and the terminal is set back. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`Terminal.test_an_empty_line_and_the_end_of_input`](../tests/test_terminal.py#L46) | Mid* / commented | Scenario: an empty line and the end of input. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |
| [`NoTerminal.test_without_a_terminal_add_key_refuses`](../tests/test_terminal.py#L62) | Mid* / commented | Scenario: without a terminal add key refuses. Disabled because no independently reviewed top-tier rationale was established for this case. Mid is provisional, not a verdict that every assertion is useful. |

## Low tier removed in the prior pass

Source remains in Git at the reviewed revision; these cases are not reintroduced as comments. Supporting evidence is in the October pruning report.

| Former test | Tier / state | Justification |
| --- | --- | --- |
| `tests/test_settings.py::SettingsFile.test_the_file_lies_in_the_arbol_folder` | Low / removed | Copies a literal Path concatenation; it exercises no selection, parsing or failure behavior. |
| `tests/test_settings.py::SettingsFile.test_a_missing_file_gives_the_defaults` | Low / removed | Repeats the default dataclass values and the same missing-settings success already exercised by the CLI. |
| `tests/test_key.py::SystemCommand.test_the_systems_security_command_and_the_item_of_cls_0` | Low / removed | Compares three imported constants with the same three source literals. |
| `tests/test_key.py::KeyCommand.test_the_remedy_says_how_to_store_the_key` | Low / removed | Copies the full remedy sentence without exercising a distinct failure; the missing helper already checks the add-key remedy. |
| `tests/test_packaging.py::Packaging.test_the_live_check_is_the_one_real_question` | Low / removed | Mocks the only delegated function and verifies its fixed return and forwarding argument. |
| `tests/test_packaging.py::Packaging.test_the_contract_check_has_its_scenarios` | Low / removed | Duplicates the scenario-name registry without exercising any scenario or checking its quality. |
| `tests/test_packaging.py::Packaging.test_the_description_names_the_three_checks` | Low / removed | Copies static descriptor names and shell-command spelling; package validation and the real gate tests are retained. |
| `tests/test_live.py::Judge.test_the_reply_names_the_model_of_info_and_holds_the_answer` | Low / removed | Repeats the same valid INFO/REPLY judgement already run by the complete private-program live-check case. |
| `tests/test_packaging.py::Packaging.test_package_metadata_must_agree` | Low / removed | Sets two version strings to unequal values and asserts the explicit equality guard; no package installation or compatibility boundary is exercised. |
| `tests/test_arguments.py::Arguments.test_commands_and_their_options` | Low / removed | Copies ordinary valid argument records and default values; execution adds little beyond the parser. |
| `tests/test_arguments.py::Arguments.test_timeout_belongs_to_classify_only` | Low / removed | Single assertion repeats the command-options membership table for info. |
| `tests/test_identity.py::Identity.test_the_record_in_the_builds_own_folder` | Low / removed | Writes a valid record and checks two fields are returned unchanged. |
| `tests/test_identity.py::Identity.test_outside_a_build_the_build_number_is_zero` | Low / removed | Checks the literal development fallback; expected_identity duplicates the same file-selection logic. |
| `tests/test_request.py::Requests.test_the_three_kinds_are_accepted` | Low / removed | Parses an ordinary valid JSON request and reads its question keys back unchanged. |
| `tests/test_request.py::SizeLimit.test_the_body_is_the_request_with_the_model_added` | Low / removed | Expected value repeats the exact dictionary-unpack expression in body_for_jev. |
| `tests/test_settings.py::SettingsFile.test_every_field_is_read` | Low / removed | Copies all ordinary settings fields into a dataclass expectation and repeats trivial defaults. |
| `tests/test_cli.py::Errors.test_the_eight_codes` | Low / removed | Copies error-enum cardinality, retry membership and envelope keys from the error wrapper. |
