"""One attempt of the call to Jev (CLS-0, "What is sent to Jev").

`POST` of the body to the endpoint, with the key as a bearer token and no other header than
the ones HTTP needs. `http.client` is used directly: it follows no proxy of the environment
and no redirect, so the request reaches the endpoint of the settings and nothing else. An
endpoint on this Mac must also be reached at a loopback address (CLS-0.13).

The attempt runs beside the main thread, which waits for it only until the time limit of the
call: a slow name lookup, connection or answer cannot hold the call past its limit (CLS-0.9).
A connection that failed is `vendor_unavailable`, which the caller may try again (CLS-0.11).
"""

import http.client
import ipaddress
import re
import ssl
import threading
from urllib.parse import urlsplit

from .errors import Failure
from .limits import Deadline
from .settings import DEFAULT_ENDPOINT

USER_AGENT = "arbol-classifier"
SECONDS = re.compile(r"[0-9]{1,6}", re.ASCII)

type Answer = tuple[int, bytes, int | None]  # the status, the body, and Retry-After in seconds when Jev named it


def on_this_mac(peer: str) -> bool:
    try:
        address = ipaddress.ip_address(peer.partition("%")[0])
    except ValueError:
        return False
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped is not None:
        return address.ipv4_mapped.is_loopback
    return address.is_loopback


def attempt(endpoint: str, body: bytes, key: str, timeout: float) -> Answer:
    """Send the body once and give the status, the body of the answer and its Retry-After."""
    parts = urlsplit(endpoint)
    host = parts.hostname or ""
    path = (parts.path or "/") + (f"?{parts.query}" if parts.query else "")
    connection = (
        http.client.HTTPSConnection(host, parts.port, timeout=timeout, context=ssl.create_default_context())
        if parts.scheme == "https"
        else http.client.HTTPConnection(host, parts.port, timeout=timeout)
    )
    try:
        connection.connect()
        peer = str(connection.sock.getpeername()[0]) if connection.sock is not None else ""
        if endpoint != DEFAULT_ENDPOINT and not on_this_mac(peer):
            raise Failure(
                "invalid_input", f"The endpoint {endpoint} does not lead to an address on this Mac. Nothing was sent."
            )
        connection.request(
            "POST",
            path,
            body=body,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": USER_AGENT},
        )
        response = connection.getresponse()
        retry_after = (response.getheader("Retry-After") or "").strip()
        return response.status, response.read(), int(retry_after) if SECONDS.fullmatch(retry_after) else None
    except TimeoutError:
        raise Failure("limit_reached", "Jev did not answer within the time limit of the call.") from None
    except (OSError, http.client.RemoteDisconnected):
        raise Failure("vendor_unavailable", f"Jev could not be reached at {endpoint}.") from None
    except http.client.HTTPException:
        raise Failure("vendor_error", "Jev's answer is not an HTTP response that can be read.") from None
    finally:
        connection.close()


def post(endpoint: str, body: bytes, key: str, deadline: Deadline) -> Answer:
    """One attempt that ends with the time limit of the call at the latest."""
    outcome: list[Answer | BaseException] = []

    def run() -> None:
        try:
            outcome.append(attempt(endpoint, body, key, max(deadline.remaining(), 0.001)))
        except BaseException as error:
            outcome.append(error)

    worker = threading.Thread(target=run, name="jev-attempt", daemon=True)
    worker.start()
    worker.join(max(deadline.remaining(), 0))
    if not outcome:
        raise deadline.reached("while Jev was asked")
    result = outcome[0]
    if isinstance(result, BaseException):
        if isinstance(result, Failure) and result.code == "limit_reached":
            raise deadline.reached("while Jev was asked") from None
        raise result
    return result
