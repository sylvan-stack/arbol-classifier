"""The settings file `~/.arbol/arbol-classifier.json` (CLS-0, "Settings").

The file is read at the start of every call and never written. It may be missing.
A faulty file refuses the call and names the file and the fault, never a value.
A key the classifier does not know refuses the file too (CLS-D5, decided by the owner on 14 October 2026).
"""

import ipaddress
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from .arguments import valid_timeout
from .errors import Failure
from .json_types import Json, loads

DEFAULT_MODEL = "jev-1.13.0"
DEFAULT_ENDPOINT = "https://api.typesafe.ai/v1/systemone"
DEFAULT_TIMEOUT_SECONDS = 10.0
DEFAULT_MAX_REQUEST_BYTES = 64000
KNOWN = ("model", "timeoutSeconds", "maxRequestBytes", "endpoint", "secret")
EXACT_MODEL = re.compile(r"jev-(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)", re.ASCII)


@dataclass(frozen=True)
class Settings:
    model: str = DEFAULT_MODEL
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    max_request_bytes: int = DEFAULT_MAX_REQUEST_BYTES
    endpoint: str = DEFAULT_ENDPOINT
    secret_command: tuple[str, ...] | None = None  # None: the classifier's Keychain item


def settings_path(home: str) -> Path:
    return Path(home) / ".arbol" / "arbol-classifier.json"


def exact_model(value: str) -> bool:
    return EXACT_MODEL.fullmatch(value) is not None


def allowed_endpoint(value: str) -> bool:
    """Jev's own address, or an address on this Mac: localhost or a loopback address."""
    if value == DEFAULT_ENDPOINT:
        return True
    if any(character.isspace() or not character.isprintable() for character in value):
        return False
    try:
        parts = urlsplit(value)
        host = parts.hostname
        _ = parts.port
    except ValueError:
        return False
    if parts.scheme not in ("http", "https") or not host:
        return False
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def read_settings(file: Path) -> Settings:
    try:
        text = file.read_text(encoding="utf-8")
    except FileNotFoundError:
        return Settings()
    except (OSError, ValueError):
        raise Failure("invalid_input", f"Cannot read the settings file {file}.") from None
    try:
        value = loads(text)
    except ValueError:
        raise Failure("invalid_input", f"The settings file {file} is not valid JSON.") from None
    if not isinstance(value, dict):
        raise Failure("invalid_input", f"The settings file {file} must hold one JSON object.")

    def fault(field: str, expected: str) -> Failure:
        return Failure("invalid_input", f"The settings file {file}: {field} must be {expected}.")

    def refuse_unknown(item: dict[str, Json], known: tuple[str, ...], prefix: str = "") -> None:
        unknown = [prefix + key for key in item if key not in known]
        if unknown:
            label = "key" if len(unknown) == 1 else "keys"
            raise Failure(
                "invalid_input", f"The settings file {file} has the unknown {label} {', '.join(unknown)}."
            )

    refuse_unknown(value, KNOWN)
    model = value.get("model", DEFAULT_MODEL)
    if not isinstance(model, str) or not exact_model(model):
        raise fault("model", "an exact Jev version, written as jev- and three numbers")
    timeout = value.get("timeoutSeconds", DEFAULT_TIMEOUT_SECONDS)
    if not valid_timeout(timeout):
        raise fault("timeoutSeconds", "a number of seconds from 1 to 60")
    assert isinstance(timeout, (int, float))
    size = value.get("maxRequestBytes", DEFAULT_MAX_REQUEST_BYTES)
    if not isinstance(size, int) or isinstance(size, bool) or size < 1:
        raise fault("maxRequestBytes", "a positive whole number")
    endpoint = value.get("endpoint", DEFAULT_ENDPOINT)
    if not isinstance(endpoint, str) or not allowed_endpoint(endpoint):
        raise fault("endpoint", f"Jev's own address {DEFAULT_ENDPOINT} or an address on this Mac")
    command: tuple[str, ...] | None = None
    if "secret" in value:
        secret = value["secret"]
        if not isinstance(secret, dict):
            raise fault("secret", 'an object with "from" set to "keychain" or "command"')
        source = secret.get("from")
        if source == "keychain":
            refuse_unknown(secret, ("from",), "secret.")
        elif source == "command":
            refuse_unknown(secret, ("from", "command"), "secret.")
            parts = secret.get("command")
            if (
                not isinstance(parts, list)
                or not parts
                or not all(isinstance(part, str) for part in parts)
                or not parts[0]
            ):
                raise fault("secret.command", "a list of texts, the program first")
            command = tuple(str(part) for part in parts)
        else:
            raise fault("secret.from", '"keychain" or "command"')
    return Settings(model, float(timeout), size, endpoint, command)
