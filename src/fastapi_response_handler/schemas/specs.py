"""Named, reusable source-of-truth definitions for success and error responses.

Define each response once, then reuse the same spec in service code
(raising exceptions, building envelopes) and OpenAPI examples, so no
message or error code is ever repeated by hand.
"""
from dataclasses import dataclass, replace
from typing import Any

from .details import ErrorDetail
from .error import ErrorResponse
from .success import SuccessResponse


@dataclass(frozen=True, slots=True)
class ErrorSpec:
    """A single error defined once: public message, code, status, and details."""

    message: str
    error_code: str | None = None
    details: tuple[ErrorDetail, ...] | None = None
    status_code: int = 500

    def response(self) -> ErrorResponse:
        """Build the standard error envelope for this spec."""
        return ErrorResponse(
            message=self.message,
            error_code=self.error_code,
            details=list(self.details) if self.details is not None else None,
        )

    def with_details(self, *details: ErrorDetail) -> "ErrorSpec":
        """Copy this spec with new details; called without arguments, details are cleared."""
        return replace(self, details=tuple(details) or None)


@dataclass(frozen=True, slots=True)
class SuccessSpec:
    """A success message defined once and reused across success endpoints."""

    message: str = "Operation completed successfully"

    def response(self, data: Any = None) -> SuccessResponse:
        """Build the standard success envelope for this spec."""
        return SuccessResponse(message=self.message, data=data)
