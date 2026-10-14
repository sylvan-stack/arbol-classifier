"""The time limit of a call and the waits between attempts (CLS-0, "Limits").

One time limit holds for the whole call, from its start: reading the request and the key,
every attempt and every wait. `SCALE` multiplies every time of a call. It is 1 in the program;
the contract check shortens the times with it (`scripts/contract_entry.py`), so that no
scenario waits for seconds.
"""

import time

from .errors import Failure

ATTEMPTS = 3
WAITS = (0.5, 1.0)  # before the second and before the third attempt
SCALE = 1.0


class Deadline:
    def __init__(self, seconds: float, started: float | None = None) -> None:
        self.seconds = seconds
        self.end = (time.monotonic() if started is None else started) + seconds * SCALE

    def remaining(self) -> float:
        return self.end - time.monotonic()

    def reached(self, during: str) -> Failure:
        return Failure("limit_reached", f"The time limit of the call, {self.seconds:g} seconds, was reached {during}.")


def wait_before(attempt: int) -> float:
    """The wait before attempt number `attempt`, counted from 0, in seconds."""
    return WAITS[attempt - 1] * SCALE
