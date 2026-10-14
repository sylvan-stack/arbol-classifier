"""Jev's reply, checked and then given as Jev gave it (CLS-0, "The request and the result").

The checks after the call: the reply is JSON, it names the model that was asked for, and it
holds an answer for every question asked and for no other. Nothing is taken away from it.
"""

from collections.abc import Iterable

from .errors import Failure
from .json_types import Object, dumps, loads


def accept_reply(data: bytes, model: str, asked: Iterable[str]) -> Object:
    try:
        value = loads(data.decode("utf-8"))
    except (ValueError, RecursionError):
        raise Failure("vendor_error", "Jev's reply is not JSON.") from None
    if not isinstance(value, dict):
        raise Failure("vendor_error", "Jev's reply is not a JSON object.")
    if value.get("model") != model:
        raise Failure("vendor_error", f"Jev's reply does not name the model that was asked for, {model}.")
    answers = value.get("answers")
    if not isinstance(answers, dict):
        raise Failure("vendor_error", "Jev's reply holds no answers.")
    names = set(asked)
    if not names <= set(answers):
        raise Failure("vendor_error", "Jev's reply lacks an answer for a question that was asked.")
    if not set(answers) <= names:
        raise Failure("vendor_error", "Jev's reply holds an answer for a question that was not asked.")
    try:
        dumps(value).encode("utf-8")
    except ValueError:
        raise Failure("vendor_error", "Jev's reply holds text that is not valid Unicode.") from None
    return value
