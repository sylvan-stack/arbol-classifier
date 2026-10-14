"""`classify`: one request, at most three attempts at Jev, the reply as Jev gave it (CLS-0.1 to 0.12).

The order keeps the key and the network out of a refusal: the request is read and its body
measured first, then the key is read, then Jev is asked. A further attempt is made only after
429, 529, another status from 500 on, or a connection that failed, after a wait of half a
second and then one second, and only when the wait ends before the time limit of the call.
"""

import time
from collections.abc import Callable, Iterable
from pathlib import Path

from .errors import Failure
from .jev import Answer, post
from .json_types import Json, Object, loads
from .key import read_key
from .limits import ATTEMPTS, Deadline, wait_before
from .reply import accept_reply
from .request import body_for_jev, question_names, read_request
from .settings import Settings

type Send = Callable[[str, bytes, str, Deadline], Answer]
type ReadKey = Callable[[Settings, Path, Deadline], str]

SAID_LIMIT = 300


def texts(value: Json) -> Iterable[str]:
    """Every text in a JSON value: the judged text is kept out of what Jev's refusal is shown as."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from texts(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from texts(item)


def jev_said(reply: bytes, hidden: Iterable[str]) -> str | None:
    """What Jev said about a refusal, in its own words: only its message fields, never what it echoes of the request."""
    try:
        value = loads(reply.decode("utf-8"))
    except (ValueError, RecursionError):
        return None
    words: list[str] = []
    if isinstance(value, dict):
        detail = value.get("detail")
        error = value.get("error")
        if isinstance(detail, list):
            for item in detail[:5]:
                if isinstance(item, dict) and isinstance(item.get("msg"), str):
                    where = item.get("loc")
                    place = ".".join(str(part) for part in where) if isinstance(where, list) else ""
                    words.append(f"{place}: {item['msg']}" if place else str(item["msg"]))
        for text in (detail, value.get("message"), error, error.get("message") if isinstance(error, dict) else None):
            if isinstance(text, str):
                words.append(text)
    said = " ".join(" ".join(words).split())
    for text in sorted(set(hidden), key=len, reverse=True):
        if len(text) >= 4:
            said = said.replace(text, "…")
    if len(said) > SAID_LIMIT:
        said = said[: SAID_LIMIT - 1] + "…"
    return said or None


def refusal(status: int, reply: bytes, retry_after: int | None, hidden: Iterable[str], attempts: int) -> Failure:
    """The failure for a status other than 200 (CLS-0, "Errors")."""
    said = jev_said(reply, hidden)
    words = f" Jev said: {said}" if said else ""
    tried = f" Attempts made: {attempts}." if attempts > 1 else ""
    if status == 401:
        return Failure("credential_rejected", f"Jev refused the key (HTTP status 401).{words}",
                       "Store a valid key with: arbol-classifier add-key", vendor_status=status)
    if status == 422:
        message = f"Jev refused the request as invalid: {said}" if said else (
            "Jev refused the request as invalid (HTTP status 422) and gave no reason that can be shown.")
        return Failure("invalid_input", message, vendor_status=status)
    if status == 413:
        return Failure("invalid_input", f"Jev refused the request as too large (HTTP status 413).{words}",
                       vendor_status=status)
    if status == 429:
        return Failure("rate_limited", f"Jev answered that too many requests were made (HTTP status 429).{tried}{words}",
                       vendor_status=status, retry_after=retry_after)
    if status == 529:
        return Failure("vendor_unavailable", f"Jev is overloaded (HTTP status 529).{tried}{words}", vendor_status=status)
    if status >= 500:
        return Failure("vendor_unavailable", f"Jev failed on its side (HTTP status {status}).{tried}{words}",
                       vendor_status=status)
    return Failure("vendor_error", f"Jev refused the request (HTTP status {status}).{words}", vendor_status=status)


def again(failure: Failure) -> bool:
    """Whether a further attempt can help: after 429, 529, another status from 500 on, or a failed connection."""
    return failure.code in ("rate_limited", "vendor_unavailable")


def classify(
    data: bytes,
    settings: Settings,
    settings_file: Path,
    deadline: Deadline,
    *,
    send: Send | None = None,
    key: ReadKey | None = None,
) -> Object:
    request = read_request(data)
    body = body_for_jev(request, settings.model, settings.max_request_bytes)
    secret = (key or read_key)(settings, settings_file, deadline)
    hidden = [secret, *texts(request["state"])]
    last: Failure | None = None
    for number in range(ATTEMPTS):
        if number:
            assert last is not None
            wait = wait_before(number)
            if deadline.remaining() <= wait:
                raise last
            time.sleep(wait)
        try:
            status, reply, retry_after = (send or post)(settings.endpoint, body, secret, deadline)
        except Failure as failure:
            if not again(failure):
                raise
            last = Failure(failure.code, f"{failure}{f' Attempts made: {number + 1}.' if number else ''}")
            continue
        if status == 200:
            return accept_reply(reply, settings.model, question_names(request))
        last = refusal(status, reply, retry_after, hidden, number + 1)
        if not again(last):
            raise last
    assert last is not None
    raise last
