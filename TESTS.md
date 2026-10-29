# Tests: arbol-classifier

Only the top-tier cases below are active. They may be selected when useful during implementation; running tests after every change is not required. Writing, restoring or running mid-tier tests requires a separate testing task explicitly requested by the owner. Do not write or restore low-tier tests.

[Mid-tier descriptions and justifications](MID_TIER.md) · [Complete inventory and tier justifications](docs/test-inventory.md) · [Machine-readable inventory](test-tiers.json)

Reviewed revision: `407a70294b8c3355cf7422f5b6b7abaf95bc7419` (28 October 2026), plus the preceding local pruning changes. No tests were run for this reset.

## Selection and limits

2 active Python definitions and 0 active standalone programs; 89 commented Python definitions. Also disabled: 0 named Node cases, 48 custom scenario functions and 0 standalone check programs. 5 broad entry points explicitly refuse. 17 low-tier cases remain removed from the prior review. These categories overlap in execution and must not be added into a runtime suite size.

Top-tier cases were individually read for the failure they observe. The remaining mid-tier labels are provisional execution decisions, not a claim that thousands of tests have passed a complete semantic review. Reassess value before restoring any of them. A browser program may contain many assertions; it is inventoried as one indivisible program, not as one asserted behavior.

## Active top tier

| Exact selector or program | Why this case earns a place |
| --- | --- |
| [`test_top_classify.Attempts.test_no_wait_goes_past_the_time_limit`](tests/top/test_top_classify.py#L14) | Puts the deadline between the first and second retry waits. Checks that the call returns the last vendor refusal after two sends instead of sleeping or retrying past the total budget. |
| [`test_top_key.StoreKey.test_the_key_goes_to_security_on_standard_input_never_as_an_argument`](tests/top/test_top_key.py#L19) | Records the security subprocess boundary and verifies the stored key through a later read. Detects credential exposure through process arguments or environment while still proving that storage worked. |

## Layout and shared support

Case bodies are separated into [`tests/top/`](tests/top/) and [`tests/mid/`](tests/mid/). The former mixed test modules retain shared fixture classes, helper functions and imports at their established paths, with no inventoried test methods. This preserves existing subprocess paths, patch targets and fixture imports without copying helpers into both tiers. Original check entry points retain their refusals.

## Running a selected top-tier case

Select an exact method when it resolves a concrete uncertainty; no run is required after an edit. The new module names begin with test_top_ so they cannot shadow the shared fixture modules. Do not run whole folders or discovery as a substitute. Original prerequisites, skips and environment limitations still apply. A focused result is not full qualification.

From the repository root, using the prepared repository interpreter:

```sh
PYTHONPATH=src:tests:tests/top python -m unittest test_top_classify.Attempts.test_no_wait_goes_past_the_time_limit
```

## Mid-tier review and restoration

[MID_TIER.md](MID_TIER.md) describes every retained mid-tier entry and its existing reason, identifies provisional classifications and explains restoration. Only a separately requested testing task may restore or run these sources. Keep the source in the mid folder; restore only the selected imports, class headers and bodies, update the inventories, and return the source to comments afterward unless the owner says otherwise. Broad entry points continue to refuse; repairing a qualification workflow requires its own explicit testing task.

Layout revision: `5cf16908e3371691f81103ae589d9d2d15a78ec4`. No tests were run for this reorganization. Previous identifiers and source lines are retained in test-tiers.json. Indexed Origin relocation and ingest remain deferred; moving files supplies no new runtime proof.
