"""`classify`: one request, one call to Jev, the reply as Jev gave it (CLS-0.1 to 0.7).

The order keeps the key and the network out of a refusal: the request is read and its body
measured first, then the key is read, then the one call is made.
"""

from collections.abc import Callable
from pathlib import Path

from .errors import Failure
from .jev import post
from .json_types import Object
from .key import read_key
from .reply import accept_reply
from .request import body_for_jev, question_names, read_request
from .settings import Settings

type Send = Callable[[str, bytes, str, float], tuple[int, bytes]]
type ReadKey = Callable[[Settings, Path, float], str]


def classify(
    data: bytes,
    settings: Settings,
    settings_file: Path,
    timeout: float,
    *,
    send: Send | None = None,
    key: ReadKey | None = None,
) -> Object:
    request = read_request(data)
    body = body_for_jev(request, settings.model, settings.max_request_bytes)
    secret = (key or read_key)(settings, settings_file, timeout)
    status, reply = (send or post)(settings.endpoint, body, secret, timeout)
    if status != 200:
        # Which code a status gets, and which statuses are tried again, comes with SYL-162.
        raise Failure("vendor_error", f"Jev answered with the HTTP status {status}.")
    return accept_reply(reply, settings.model, question_names(request))
