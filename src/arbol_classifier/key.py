"""Where the Jev key comes from (CLS-0, "The key").

At each call the key is read from the classifier's Keychain item with the system's `security`
command, or from the command that the settings name. `add-key` is the one place that writes the
item, and nothing removes it. The key is never an argument and never part of a message:
`security` prints it on a pipe, and `add-key` hands it to `security` on standard input.
"""

import subprocess
from pathlib import Path

from .errors import Failure
from .limits import Deadline
from .settings import Settings

SECURITY = "/usr/bin/security"
SERVICE = "com.sylvan-stack.arbol.classifier"
ACCOUNT = "jev"
NOT_FOUND = 44  # the status of `security` for an item that does not exist
STORE_SECONDS = 60.0  # add-key: time for the Keychain, which may ask the person to unlock it
VISIBLE = frozenset(chr(code) for code in range(0x21, 0x7F))
STORE_REMEDY = "Store the key with: arbol-classifier add-key"


def can_be_key(value: str) -> bool:
    """One line of visible characters without spaces (CLS-0, "Errors")."""
    return bool(value) and set(value) <= VISIBLE


def time_left(deadline: Deadline) -> float:
    remaining = deadline.remaining()
    if remaining <= 0:
        raise subprocess.TimeoutExpired("", deadline.seconds)
    return remaining


def run(command: list[str], deadline: Deadline, data: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    """Run a command that has until the deadline; with no input its standard input is empty."""
    if data is None:
        return subprocess.run(
            command, stdin=subprocess.DEVNULL, capture_output=True, timeout=time_left(deadline), check=False
        )
    return subprocess.run(command, input=data, capture_output=True, timeout=time_left(deadline), check=False)


def security(args: list[str], deadline: Deadline, data: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    return run([SECURITY, *args], deadline, data)


def read_key(settings: Settings, settings_file: Path, deadline: Deadline) -> str:
    if settings.secret_command is not None:
        return key_from_command(settings.secret_command, settings_file, deadline)
    return key_from_keychain(deadline)


def key_found(settings: Settings, settings_file: Path, timeout: float) -> bool:
    """Whether a key is found where `classify` would look for it, within `timeout`; the key itself is dropped."""
    try:
        read_key(settings, settings_file, Deadline(timeout))
    except Failure as failure:
        if failure.code in ("not_signed_in", "limit_reached"):
            return False
        raise
    return True


def key_from_keychain(deadline: Deadline) -> str:
    where = (
        "No Jev API key was found. arbol-classifier looked in the login Keychain for the item with the service "
        f"{SERVICE} and the account {ACCOUNT}"
    )

    def missing(why: str | None = None) -> Failure:
        return Failure("not_signed_in", f"{where}, and {why}." if why else f"{where}.", STORE_REMEDY)

    try:
        result = security(["find-generic-password", "-s", SERVICE, "-a", ACCOUNT, "-w"], deadline)
    except subprocess.TimeoutExpired:
        raise deadline.reached("while the Jev API key was read from the login Keychain") from None
    except (OSError, ValueError):
        raise missing(f"the system's command {SECURITY} could not be started") from None
    if result.returncode == NOT_FOUND:
        raise missing()
    if result.returncode != 0:
        raise missing(f"the item could not be read: security ended with status {result.returncode}")
    key = result.stdout.decode("utf-8", "replace").strip()
    if not key:
        raise missing("the item is empty")
    if not can_be_key(key):
        raise missing("what the item holds cannot be a key, which is one line of visible characters without spaces")
    return key


def key_from_command(command: tuple[str, ...], settings_file: Path, deadline: Deadline) -> str:
    where = f"arbol-classifier ran the command that the settings file {settings_file} names for the key"
    remedy = (
        f"Correct secret.command in the settings file {settings_file}, or remove secret from it and store the key "
        "with: arbol-classifier add-key"
    )

    def missing(why: str) -> Failure:
        return Failure("not_signed_in", f"No Jev API key was found. {where}, and it {why}.", remedy)

    try:
        result = run(list(command), deadline)
    except subprocess.TimeoutExpired:
        raise deadline.reached(f"while the command that the settings file {settings_file} names for the key ran") from None
    except (OSError, ValueError):
        raise missing("could not be started") from None
    if result.returncode != 0:
        raise missing("failed")
    key = result.stdout.decode("utf-8", "replace").strip()
    if not key:
        raise missing("printed nothing")
    if not can_be_key(key):
        raise missing("printed something that is not a key: one line of visible characters")
    return key


def quoted(value: str) -> str:
    """A word of a `security -i` line: in double quotes, with a backslash before a backslash or a quote."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def store_key(key: str, seconds: float = STORE_SECONDS) -> bool:
    """Store the key in the item, replacing a key stored there before; give whether one was replaced.

    The key goes to `security` as a line on its standard input, so it is never one of the arguments
    of a running program. The key is read back once to see that the Keychain kept it.
    """
    if not can_be_key(key):
        raise ValueError("Only a key that can be one is stored.")
    place = f"the login Keychain, the item with the service {SERVICE} and the account {ACCOUNT}"

    def not_stored(why: str) -> Failure:
        return Failure("internal", f"The key could not be stored in {place}: {why}.")

    line = f"add-generic-password -U -s {quoted(SERVICE)} -a {quoted(ACCOUNT)} -w {quoted(key)}\n"
    deadline = Deadline(seconds)
    try:
        found = security(["find-generic-password", "-s", SERVICE, "-a", ACCOUNT], deadline)
        if found.returncode not in (0, NOT_FOUND):
            raise not_stored(f"the Keychain could not be searched, security ended with status {found.returncode}")
        stored = security(["-i"], deadline, line.encode("utf-8"))
        if stored.returncode != 0:
            raise not_stored(f"security ended with status {stored.returncode}")
        kept = key_from_keychain(deadline)
    except subprocess.TimeoutExpired:
        raise not_stored(f"the Keychain did not answer within {seconds:g} seconds") from None
    except (OSError, ValueError):
        raise not_stored(f"the system's command {SECURITY} could not be started") from None
    except Failure as failure:
        if failure.code == "internal":
            raise
        if failure.code == "limit_reached":
            raise not_stored(f"the Keychain did not answer within {seconds:g} seconds") from None
        raise not_stored("the item does not hold the key when it is read back") from None
    if kept != key:
        raise not_stored("the item does not hold the key when it is read back")
    return found.returncode == 0
