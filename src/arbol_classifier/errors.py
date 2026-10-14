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
    vendor_status: int | None
    retry_after: int | None

    def __init__(
        self,
        code: str,
        message: str,
        remedy: str | None = None,
        *,
        vendor_status: int | None = None,
        retry_after: int | None = None,
    ) -> None:
        if code not in CODES:
            raise ValueError(f"Unknown classifier error code {code}.")
        super().__init__(message)
        self.code = code
        self.remedy = remedy
        self.vendor_status = vendor_status
        self.retry_after = retry_after if code == "rate_limited" else None

    def error(self) -> Object:
        result: Object = {"code": self.code, "message": str(self), "retryable": self.code in RETRYABLE}
        if self.retry_after is not None:
            result["retryAfterSeconds"] = self.retry_after
        if self.remedy is not None:
            result["remedy"] = self.remedy
        if self.vendor_status is not None:
            result["detail"] = {"basis": "fields", "vendorStatus": self.vendor_status}
        return result
