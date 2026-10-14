"""The error object of DRV-4, with the eight codes CLS-0 allows."""

from .json_types import Object

CODES = (
    "invalid_input",
    "not_signed_in",
    "credential_rejected",
    "rate_limited",
    "vendor_unavailable",
    "vendor_error",
    "limit_reached",
    "internal",
)
RETRYABLE = ("rate_limited", "vendor_unavailable")


class Failure(Exception):
    code: str
    remedy: str | None

    def __init__(self, code: str, message: str, remedy: str | None = None) -> None:
        if code not in CODES:
            raise ValueError(f"Unknown classifier error code {code}.")
        super().__init__(message)
        self.code = code
        self.remedy = remedy

    def error(self) -> Object:
        result: Object = {"code": self.code, "message": str(self), "retryable": self.code in RETRYABLE}
        if self.remedy is not None:
            result["remedy"] = self.remedy
        return result
