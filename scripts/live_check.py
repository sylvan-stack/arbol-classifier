"""The live check of CLS-0.15: one real `choice` question to Jev with the real key.

It starts the Build's own program, `bin/arbol-classifier`, as a caller would: with the person's
home folder, and so with their settings file and their Keychain item. It asks `info` for the
model and the address, then asks Jev one question of the kind `choice`: the example of CLS-0, so
that no text of anyone's goes to Jev. It passes when the call succeeds, the reply names the model
that `info` names, and it holds an answer that chooses one of the options asked. The settings
must name Jev's own address: a stand-in for Jev on this Mac cannot pass this check.

What it learned goes to standard output, which `arbol-builds` keeps in the Build's log: the
model, the answer, how long the call took and how many tokens it used. The key is read by the
program and never seen here, and a refusal is shown as the program printed it, which never
holds the key.

`ARBOL_CLASSIFIER_LIVE_SECURITY`, when set, names a program that takes the place of
`/usr/bin/security`, such as the stand-in for `security` with no item in it. The program is then
started through `contract_entry.py`, with times unchanged. It is there to prove that a Build made
while no key is stored fails this check, without touching the person's Keychain item. It cannot
make the check pass without a key that Jev accepts, since the question still goes to Jev itself.
"""

from __future__ import annotations

import json
import os
import pwd
import subprocess
from pathlib import Path
from typing import Any

JEV = "https://api.typesafe.ai/v1/systemone"
SECURITY_SWITCH = "ARBOL_CLASSIFIER_LIVE_SECURITY"
OPTIONS = ("request", "question", "other")
REQUEST: dict[str, Any] = {
    "state": "Can you also update the README while you are at it?",
    "questions": {
        "kind": {
            "type": "choice",
            "instructions": "What is this message?",
            "criteria": {
                "request": "It asks for work to be done",
                "question": "It asks for information only",
                "other": None,
            },
        }
    },
}
SECONDS = 90  # a net under the program's own time limit, which ends every call within 60 seconds


class LiveFailure(Exception):
    pass


def environment() -> dict[str, str]:
    """The person's home folder and nothing of the environment the build runs in."""
    person = pwd.getpwuid(os.getuid())
    return {"HOME": person.pw_dir, "USER": person.pw_name, "LOGNAME": person.pw_name, "PATH": "/usr/bin:/bin",
            "LANG": "en_US.UTF-8"}


def command(folder: Path, security: str | None, *args: str) -> list[str]:
    if security is None:
        return [str(folder / "bin/arbol-classifier"), *args]
    return [str(folder / "runtime/python/bin/python3.14"), "-I", "-B", str(folder / "scripts/contract_entry.py"),
            security, "1.0", *args]


def call(folder: Path, security: str | None, *args: str, data: bytes = b"") -> tuple[int, dict[str, Any]]:
    try:
        result = subprocess.run(command(folder, security, *args), input=data, capture_output=True,
                                env=environment(), cwd=environment()["HOME"], timeout=SECONDS, check=False)
    except subprocess.TimeoutExpired:
        raise LiveFailure(f"`{args[0]}` did not end within {SECONDS} seconds.") from None
    try:
        document = json.loads(result.stdout.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise LiveFailure(f"`{args[0]}` did not print one JSON document (exit status {result.returncode}).") from None
    if not isinstance(document, dict):
        raise LiveFailure(f"`{args[0]}` did not print a JSON object.")
    return result.returncode, document


def refused(name: str, status: int, document: dict[str, Any]) -> LiveFailure:
    error = document.get("error")
    if isinstance(error, dict):
        remedy = f" Remedy: {error['remedy']}" if isinstance(error.get("remedy"), str) else ""
        return LiveFailure(f"`{name}` ended with {error.get('code')}: {error.get('message')}{remedy}")
    return LiveFailure(f"`{name}` ended with exit status {status} and no error object.")


def judge(info: dict[str, Any], result: dict[str, Any]) -> str:
    """Whether Jev's reply names the model of `info` and holds the answer; what it used, in words."""
    model = info.get("model")
    if result.get("model") != model:
        raise LiveFailure(f"The reply names the model {result.get('model')!r}, not {model!r}.")
    answers = result.get("answers")
    if not isinstance(answers, dict) or set(answers) != {"kind"} or not isinstance(answers["kind"], dict):
        raise LiveFailure("The reply does not hold exactly the one answer asked for.")
    answer = answers["kind"]
    choice, confidence = answer.get("choice"), answer.get("confidence")
    if answer.get("type") != "choice" or choice not in OPTIONS:
        raise LiveFailure(f"The answer chooses none of the options asked: {choice!r}.")
    if isinstance(confidence, bool) or not isinstance(confidence, int | float) or not 0 <= confidence <= 1:
        raise LiveFailure(f"The answer's confidence is not a number from 0 to 1: {confidence!r}.")
    usage = result.get("usage")
    tokens = "Jev reported no usage"
    if isinstance(usage, dict):
        tokens = f"tokens used: {usage.get('input_tokens')} of input, {usage.get('output_tokens')} of output"
    return f"Jev answered with {model}: choice {choice!r}, confidence {confidence}; {tokens}."


# TEST-TIER-DISABLED-BEGIN scripts/live_check.py::run_live
# def run_live(folder: Path) -> int:
#     security = os.environ.get(SECURITY_SWITCH)
#     try:
#         if security is not None:
#             if not Path(security).is_absolute() or not os.access(security, os.X_OK):
#                 raise LiveFailure(f"{SECURITY_SWITCH} must name an executable file by its absolute path.")
#             print(f"live: {security} takes the place of /usr/bin/security ({SECURITY_SWITCH}).", flush=True)
#         status, info = call(folder, security, "info")
#         if status != 0:
#             raise refused("info", status, info)
#         if info.get("endpoint") != JEV:
#             raise LiveFailure(f"The settings name the endpoint {info.get('endpoint')}; the live check asks Jev "
#                               f"itself, at {JEV}.")
#         if info.get("keyFound") is not True:
#             print("live: `info` found no Jev key; `classify` is asked anyway, so that its own refusal is shown.",
#                   flush=True)
#         started = time.monotonic()
#         status, result = call(folder, security, "classify", data=json.dumps(REQUEST).encode("utf-8"))
#         seconds = time.monotonic() - started
#         if status != 0 or "error" in result:
#             raise refused("classify", status, result)
#         print(f"live: passed in {seconds:.2f} s. {judge(info, result)}", flush=True)
#         return 0
#     except LiveFailure as failure:
#         print(f"live: failed. {failure}", flush=True)
#         return 1
# TEST-TIER-DISABLED-END scripts/live_check.py::run_live
def run_live(folder: Path) -> int:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL

# Archived complete imports; restore needed names in their original scope, not at this file tail.
# TEST-TIER-IMPORTS-BEGIN scripts/live_check.py:28
# import time
# TEST-TIER-IMPORTS-END scripts/live_check.py:28
