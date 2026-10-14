"""The one call to Jev (CLS-0, "What is sent to Jev").

`POST` of the body to the endpoint, with the key as a bearer token and no other header than
the ones HTTP needs. `http.client` is used directly: it follows no proxy of the environment
and no redirect, so the request reaches the endpoint of the settings and nothing else. An
endpoint on this Mac must also be reached at a loopback address (CLS-0.13).

One attempt. The attempts, the time limit of the whole call and the table of errors come
with SYL-162.
"""

import http.client
import ipaddress
import ssl
from urllib.parse import urlsplit

from .errors import Failure
from .settings import DEFAULT_ENDPOINT

USER_AGENT = "arbol-classifier"


def on_this_mac(peer: str) -> bool:
    try:
        address = ipaddress.ip_address(peer.partition("%")[0])
    except ValueError:
        return False
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped is not None:
        return address.ipv4_mapped.is_loopback
    return address.is_loopback


def post(endpoint: str, body: bytes, key: str, timeout: float) -> tuple[int, bytes]:
    """Send the body and give the status and the body of the answer."""
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
        return response.status, response.read()
    except TimeoutError:
        raise Failure("limit_reached", f"Jev did not answer within {timeout:g} seconds.") from None
    except OSError:
        raise Failure("vendor_unavailable", f"Jev could not be reached at {endpoint}.") from None
    except http.client.HTTPException:
        raise Failure("vendor_error", "Jev's answer is not an HTTP response that can be read.") from None
    finally:
        connection.close()
