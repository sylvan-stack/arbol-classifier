"""Check the program in its final Build folder, without starting a launcher."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_support import COMPONENT, ENTRY, build_folder, digest, metadata, read_object, run, target  # noqa: E402


def verify(folder: Path, candidate: bool) -> dict[str, Any]:
    version, pin = metadata(folder)
    manifest = read_object(folder / "package-manifest.json")
    if (manifest.get("format") != 1 or manifest.get("component") != COMPONENT
            or manifest.get("entry") != ENTRY or manifest.get("packageVersion") != version
            or manifest.get("candidate") is not candidate):
        raise ValueError("The package manifest does not match this component and delivery mode.")
    if candidate:
        if manifest.get("build") != "0" or (folder / "build.json").exists():
            raise ValueError("A development candidate must use Build 0 outside the registry.")
    elif read_object(folder / "build.json").get("build") != manifest.get("build"):
        raise ValueError("The package manifest must agree with the Build record's number.")
    python = manifest.get("python")
    if not isinstance(python, dict) or python.get("version") != pin["version"] or python.get("target") != target():
        raise ValueError("The package interpreter must match the pinned version and this machine's architecture.")
    distribution = pin["distributions"][target()]
    if (python.get("archiveSha256") != distribution["sha256"] or python.get("archiveUrl") != distribution["url"]
            or python.get("provider") != pin["provider"] or python.get("release") != pin["release"]):
        raise ValueError("The package interpreter must match the pinned distribution digest and URL.")
    interpreter = folder / "runtime/python/bin/python3.14"
    if digest(interpreter) != python.get("executableSha256"):
        raise ValueError("The packaged Python executable has changed.")
    files = manifest.get("files")
    if not isinstance(files, dict):
        raise ValueError("The package manifest must record packaged file digests.")
    for relative, expected in files.items():
        if not isinstance(relative, str) or not isinstance(expected, str):
            raise ValueError("Invalid package manifest file digest.")
        path = folder / relative
        if folder not in path.resolve().parents or digest(path) != expected:
            raise ValueError(f"The packaged file {relative} is outside its folder or has changed.")
    entry = folder / ENTRY
    if entry.resolve() != entry or not entry.is_file() or not os.access(entry, os.X_OK):
        raise ValueError("The Build entry must be an executable file inside its folder.")
    probe = subprocess.run([str(interpreter), "-I", "-B", "-c", "import platform; print(platform.python_version())"],
                           check=True, cwd=folder, capture_output=True, text=True)
    if probe.stdout.strip() != pin["version"]:
        raise ValueError("The package interpreter reports the wrong Python version.")
    return manifest


# TEST-TIER-DISABLED-BEGIN scripts/check_build.py::unit
# def unit(folder: Path, number: str | None) -> int:
#     sys.path.insert(0, str(folder))
#     sys.path.insert(0, str(folder / "src"))
#     os.chdir(folder)
#     suite = unittest.TestLoader().discover(str(folder / "tests"))
#     if suite.countTestCases() == 0:
#         raise ValueError("The packaged unit check discovered no tests.")
#     return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
# TEST-TIER-DISABLED-END scripts/check_build.py::unit
def unit(folder: Path, number: str | None) -> int:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


# TEST-TIER-DISABLED-BEGIN scripts/check_build.py::contract
# def contract(folder: Path, number: str | None) -> int:
#     from contract_checks import run_contract
#
#     version, _ = metadata(folder)
#     return run_contract(folder / ENTRY, folder, version, number or "0")
# TEST-TIER-DISABLED-END scripts/check_build.py::contract
def contract(folder: Path, number: str | None) -> int:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


# TEST-TIER-DISABLED-BEGIN scripts/check_build.py::live
# def live(folder: Path, number: str | None) -> int:
#     from live_check import run_live
#
#     return run_live(folder)
# TEST-TIER-DISABLED-END scripts/check_build.py::live
def live(folder: Path, number: str | None) -> int:
    raise RuntimeError('Tests are commented under the tier policy; see TESTS.md. Restore only in an explicitly requested testing task.')  # TEST-TIER-REFUSAL


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("metadata", "unit", "contract", "live"))
    parser.add_argument("--candidate", help="Absolute development candidate folder")
    arguments = parser.parse_args()
    try:
        folder, number = build_folder(arguments.candidate)
        manifest = verify(folder, arguments.candidate is not None)
        interpreter = (folder / "runtime/python/bin/python3.14").resolve()
        if arguments.mode in ("unit", "contract") and Path(sys.executable).resolve() != interpreter:
            return run([str(interpreter), "-I", "-B", str(folder / "scripts/check_build.py"), arguments.mode,
                        *(["--candidate", str(folder)] if arguments.candidate else [])], cwd=folder)
        if arguments.mode == "metadata":
            print(json.dumps({"component": COMPONENT, "entry": ENTRY, "python": manifest["python"], "passed": True}))
            return 0
        return {"unit": unit, "contract": contract, "live": live}[arguments.mode](folder, number)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"Cannot check {COMPONENT}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

# Archived complete imports; restore needed names in their original scope, not at this file tail.
# TEST-TIER-IMPORTS-BEGIN scripts/check_build.py:10
# import unittest
# TEST-TIER-IMPORTS-END scripts/check_build.py:10
