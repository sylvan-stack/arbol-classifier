# Arbol Classifier

Arbol Classifier: a component of Arbol 2. An Arbol Trunk starts it to have a text judged: it takes the text and a list of questions with their allowed answers, asks Jev, and gives for each question the chosen answer and its confidence.

Its specification is CLS-0, `~/Artifacts/arbol-classifier/specs/00-the-classifier.md`.

| | |
|---|---|
| Package | `@sylvan-stack/arbol-classifier` 1.0.0 |
| Artifact corpus | `~/Artifacts/arbol-classifier` (GitHub `sylvan-stack/arbol-classifier-artifacts`) |

## What works

From SYL-152: the program, its settings and `info`. From SYL-157: `classify`, from the request to Jev's reply.

```sh
arbol-classifier info
arbol-classifier info --settings ./test-settings.json
arbol-classifier classify < request.json
arbol-classifier classify --timeout 5 --settings ./test-settings.json < request.json
```

`classify` reads one request in Jev's own form on standard input: a `state` and named `questions` of the kinds `choice`, `noul` and `score`. It checks only what CLS-0 lists (one JSON object, a `state`, at least one question, a `type` and `instructions` in each, no `model`) and interprets no question. It adds `model`, measures the body as it is sent against `maxRequestBytes`, and sends it with one `POST` to the endpoint, the key as a bearer token. The reply is printed as Jev gave it, after the check that it names the model asked for and holds an answer for every question asked and for no other.

Until SYL-161 the key comes only from a command that the settings name (`"secret": {"from": "command", "command": [...]}`); the Keychain item, the default, answers `internal`. Until SYL-162 there is one attempt, the time limit applies to each step of the connection, and a status other than 200 is a `vendor_error`.

`info` prints one JSON document: its name, the package version, the build number, the version of its contract (1), its settings file, the Jev model it uses, the address it calls, and `keyFound`, which stays `false` until the key is read (SYL-161). A refusal prints `{ "error": … }` with the error object of DRV-4 and ends with status 1. `-v <build number>` belongs to the launcher, not to the program.

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
| `unit` | The packaged unit tests, with the packaged interpreter, without network and without the Keychain |
| `contract` | `scripts/contract_checks.py`: starts the built program with a fresh home folder and checks what it prints. From SYL-152: `info`, the settings file and the refusals of the command line. From SYL-157: `classify` against the stand-in for Jev, `scripts/jev_stand_in.py`, a small server on the loopback address that answers by a script and records what it was sent |
| `live` | One real question to Jev. It does not exist before SYL-164 and fails, so no Build counts as working yet |

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
