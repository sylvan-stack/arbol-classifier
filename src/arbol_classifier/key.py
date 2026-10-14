"""Where the Jev key comes from (CLS-0, "The key").

From SYL-157 on the key comes from the command that the settings name. The Keychain item,
the default, comes with SYL-161. The key is never part of a message.
"""

import subprocess
from pathlib import Path

from .errors import Failure
from .settings import Settings

VISIBLE = frozenset(chr(code) for code in range(0x21, 0x7F))


def read_key(settings: Settings, settings_file: Path, timeout: float) -> str:
    if settings.secret_command is None:
        raise Failure("internal", "Reading the Jev key from the Keychain is not part of this Build yet.")
    where = f"arbol-classifier ran the command that the settings file {settings_file} names for the key"
    remedy = f"Correct secret.command in the settings file {settings_file}."

    def missing(why: str) -> Failure:
        return Failure("not_signed_in", f"No Jev API key was found. {where}, and it {why}.", remedy)

    try:
        result = subprocess.run(
            list(settings.secret_command), stdin=subprocess.DEVNULL, capture_output=True, timeout=timeout, check=False
        )
    except subprocess.TimeoutExpired:
        raise missing(f"did not end within {timeout:g} seconds") from None
    except (OSError, ValueError):
        raise missing("could not be started") from None
    if result.returncode != 0:
        raise missing("failed")
    key = result.stdout.decode("utf-8", "replace").strip()
    if not key:
        raise missing("printed nothing")
    if not set(key) <= VISIBLE:
        raise missing("printed something that is not a key: one line of visible characters")
    return key
