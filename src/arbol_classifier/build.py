"""Which Build runs: BLD-0.12 and 0.14.

The package version and the build number come from the record `build.json` in the
Build's own folder. Outside a Build's folder, as in development, the version comes
from `pyproject.toml` and the build number is `0`.
"""

import re
import tomllib
from pathlib import Path

from . import NAME
from .errors import Failure
from .json_types import loads

BUILD_NUMBER = re.compile(r"[1-9a-f][0-9a-f]*", re.ASCII)
PACKAGE_VERSION = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?", re.ASCII)


def build_identity(start: Path | None = None) -> tuple[str, str]:
    """The package version and the build number of the Build that runs."""
    directory = start or Path(__file__).resolve().parent
    for folder in (directory, *directory.parents):
        record_file = folder / "build.json"
        if record_file.exists():
            try:
                record = loads(record_file.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                raise Failure("internal", f"Cannot read the Build record {record_file}.") from None
            if (
                not isinstance(record, dict)
                or record.get("component") != NAME
                or not isinstance(record.get("build"), str)
                or BUILD_NUMBER.fullmatch(str(record["build"])) is None
                or not isinstance(record.get("packageVersion"), str)
                or PACKAGE_VERSION.fullmatch(str(record["packageVersion"])) is None
            ):
                raise Failure("internal", f"The Build record {record_file} is not a record of {NAME}.")
            return str(record["packageVersion"]), str(record["build"])
        project_file = folder / "pyproject.toml"
        if project_file.exists():
            try:
                project = tomllib.loads(project_file.read_text(encoding="utf-8")).get("project", {})
            except (OSError, ValueError):
                raise Failure("internal", f"Cannot read the package version in {project_file}.") from None
            if project.get("name") == NAME and isinstance(project.get("version"), str):
                return str(project["version"]), "0"
    raise Failure("internal", f"{NAME} found neither its Build record nor its package version.")
