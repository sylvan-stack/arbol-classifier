# Arbol Classifier

Arbol Classifier: a component of Arbol 2. An Arbol Trunk starts it to have a text judged: it takes the text and a list of questions with their allowed answers, asks Jev, and gives for each question the chosen answer and its confidence.

Its specification is CLS-0, `~/Artifacts/arbol-classifier/specs/00-the-classifier.md`.

| | |
|---|---|
| Package | `@sylvan-stack/arbol-classifier` 1.0.0 |
| Artifact corpus | `~/Artifacts/arbol-classifier` (GitHub `sylvan-stack/arbol-classifier-artifacts`) |

## What it does

It has three commands: `classify` has one request judged by Jev, `info` says which Build runs and with which settings, and `add-key` stores the Jev key. Every part of CLS-0 is built and checked, and a Build counts as working only after one real question to Jev.

```sh
arbol-classifier info
arbol-classifier info --settings ./test-settings.json
arbol-classifier classify < request.json
arbol-classifier classify --timeout 5 --settings ./test-settings.json < request.json
arbol-classifier add-key
```

`classify` reads one request in Jev's own form on standard input: a `state` and named `questions` of the kinds `choice`, `noul` and `score`. It checks only what CLS-0 lists (one JSON object, a `state`, at least one question, a `type` and `instructions` in each, no `model`) and interprets no question. It adds `model`, measures the body as it is sent against `maxRequestBytes`, and sends it with one `POST` to the endpoint, the key as a bearer token. The reply is printed as Jev gave it, after the check that it names the model asked for and holds an answer for every question asked and for no other.

The key is read at each call from the generic password in the login Keychain with the service `com.sylvan-stack.arbol.classifier` and the account `jev`, with `/usr/bin/security`; or, when the settings name one (`"secret": {"from": "command", "command": [...]}`), from a command that prints it. Without a key the call ends with `not_signed_in` before anything is sent: the message says that no Jev API key was found and where it was looked for, and the remedy says how to store it. The key appears in no argument, environment variable, output or diagnostic.

One time limit holds for the whole call, from its start: reading the request and the key, every attempt and every wait. It is 10 seconds, or `timeoutSeconds` in the settings, or `--timeout` (1 to 60); when it is reached the call ends with `limit_reached`. Jev is asked at most three times: a further attempt only after 429, 529, another status from 500 on, or a connection that failed, after a wait of half a second and then one second, and only when the wait ends before the time limit; otherwise the call ends with what the last attempt gave. 401 is `credential_rejected`, 422 and 413 are `invalid_input` with what Jev said (its message fields only, never what it echoes of the request, and never the judged text or the key), 429 is `rate_limited` with `retryAfterSeconds` when Jev sent `Retry-After` in seconds, 529 and 5xx are `vendor_unavailable`, any other status is `vendor_error`. Each of these errors names Jev's status in `detail.vendorStatus`.

`add-key` asks for the key at the terminal (`/dev/tty`) with echo off, and stores it in that item, replacing a key stored there before. It prints `{"keychain": {"service": …, "account": "jev"}, "replaced": …}`. The key goes to `security -i` as a line on its standard input, never as an argument, because the arguments of a running program can be read by other programs. Without a terminal, or when nothing that can be a key was typed, it refuses with `invalid_input`. Nothing in the classifier removes the item.

`info` prints one JSON document: its name, the package version, the build number, the version of its contract (1), its settings file, the Jev model it uses, the address it calls, and `keyFound`, whether a key is found where `classify` would look for it, never the key. A refusal prints `{ "error": … }` with the error object of DRV-4 and ends with status 1. `-v <build number>` belongs to the launcher, not to the program.

The settings file is `~/.arbol/arbol-classifier.json`, or the file named with `--settings`. It may be missing, and it is never written:

```json
{
  "model": "jev-1.13.0",
  "timeoutSeconds": 10,
  "maxRequestBytes": 64000,
  "endpoint": "https://api.typesafe.ai/v1/systemone",
  "secret": { "from": "keychain" }
}
```

`model` must be an exact Jev version, `jev-` and three numbers. `timeoutSeconds` takes 1 to 60, as `--timeout` does. `endpoint` is Jev's own address or an address on this Mac (`localhost` or a loopback address). A faulty file, or a key the classifier does not know, refuses the call with `invalid_input` and names the file and the field, never its value.

The program writes no file. It runs with Python's `-B`, and its Build carries bytecode made when it was packaged.

## Development

Typed Python on CPython 3.14.8, laid out as `arbol-codex-driver` is. uv prepares the development tools; the program itself uses only the standard library.

```sh
uv sync --locked --group dev
uv run --no-sync ruff check src/arbol_classifier tests scripts bin/entry.py
uv run --no-sync mypy
PYTHONPATH=src uv run --no-sync python -B -m unittest discover -s tests
bin/arbol-classifier info
```

## Builds

`arbol-builds build arbol-classifier` builds a numbered Build as `arbol-build.json` says: it syncs the tools, runs Ruff and mypy, and `scripts/package_build.py` puts the pinned standalone CPython, the program, its tests and its check scripts into the Build's folder. Then it runs three checks against the Build's own program:

| Check | What it runs |
|---|---|
| `unit` | The packaged unit tests, with the packaged interpreter, without network and without the Keychain: `scripts/security_stand_in.py` takes the place of `/usr/bin/security` and keeps its items in a folder of its own |
| `contract` | `scripts/contract_checks.py`: starts the built program with a fresh home folder and checks what it prints. From SYL-152: `info`, the settings file and the refusals of the command line. From SYL-157: `classify` against the stand-in for Jev, `scripts/jev_stand_in.py`, a small server on the loopback address that answers by a script and records what it was sent. From SYL-161: the key from the Keychain item or the key command, `not_signed_in`, and `add-key` at a pretend terminal. From SYL-162: every row of the table of errors, the attempts, the waits and the time limit, with a stand-in for Jev that can refuse, drop the connection, hold its answer or send it one byte at a time. The program is started through `scripts/contract_entry.py`, which puts the stand-in for `security` in the place of `/usr/bin/security`, so the check never reaches the real Keychain, and which multiplies every time of a call by a scale, so a scenario about time takes a fraction of a second; the scenario `cli.build-entry` starts `bin/arbol-classifier` itself, with a key command |
| `live` | `scripts/live_check.py`: one real `choice` question to Jev with the real key, which costs a fraction of a cent. It starts the Build's own `bin/arbol-classifier` with the person's home folder and nothing else of the environment, so with their settings file and their Keychain item: first `info`, then `classify` with the example question of CLS-0. It passes when the reply names the model that `info` names and chooses one of the options asked. The settings must name Jev's own address, so a stand-in for Jev cannot pass it. It writes the model, the answer, the time and the tokens used into the Build's log. Without a key, `classify` refuses with `not_signed_in`, the check fails, and so does the Build |

A Build counts as working only when all three pass. To see a build fail the `live` check for want of a key, without touching the Keychain item, name an executable that takes the place of `/usr/bin/security` in `ARBOL_CLASSIFIER_LIVE_SECURITY`, such as the stand-in for `security` with no item in it. The live check then starts the program through `scripts/contract_entry.py` with times unchanged. This can only take the key away: the question still goes to Jev itself.

A development candidate outside the registry:

```sh
uv run --no-sync python scripts/package_build.py --candidate /absolute/empty/folder
/absolute/empty/folder/runtime/python/bin/python3.14 -I -B /absolute/empty/folder/scripts/check_build.py unit --candidate /absolute/empty/folder
/absolute/empty/folder/runtime/python/bin/python3.14 -I -B /absolute/empty/folder/scripts/check_build.py contract --candidate /absolute/empty/folder
```

## Sylvan Stack 2

| Repository | Package | Version | Artifact corpus | Artifact repository |
|---|---|---|---|---|
| `arbol` | `@sylvan-stack/arbol` | 2.0.0 | `~/Artifacts/arbol` | `sylvan-stack/arbol-artifacts` |
| `arbol-root` | `@sylvan-stack/arbol-root` | 1.0.0 | `~/Artifacts/arbol-root` | `sylvan-stack/arbol-root-artifacts` |
| `arbol-trunk` | `@sylvan-stack/arbol-trunk` | 1.0.0 | `~/Artifacts/arbol-trunk` | `sylvan-stack/arbol-trunk-artifacts` |
| `arbol-claude-driver` | `@sylvan-stack/arbol-claude-driver` | 1.0.0 | `~/Artifacts/arbol-claude-driver` | `sylvan-stack/arbol-claude-driver-artifacts` |
| `arbol-codex-driver` | `@sylvan-stack/arbol-codex-driver` | 1.0.0 | `~/Artifacts/arbol-codex-driver` | `sylvan-stack/arbol-codex-driver-artifacts` |
| `arbol-classifier` | `@sylvan-stack/arbol-classifier` | 1.0.0 | `~/Artifacts/arbol-classifier` | `sylvan-stack/arbol-classifier-artifacts` |
| `mycel` | `@sylvan-stack/mycel` | 2.0.0 | `~/Artifacts/mycel` | `sylvan-stack/mycel-artifacts` |
| `arbol-pi-driver` | `@sylvan-stack/arbol-pi-driver` | 1.0.0 | `~/Artifacts/arbol-pi-driver` | `sylvan-stack/arbol-pi-driver-artifacts` |
