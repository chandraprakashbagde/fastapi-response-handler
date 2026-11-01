"""Standard error envelope."""
from typing import Literal

from pydantic import BaseModel

from .details import ErrorDetail


class ErrorResponse(BaseModel):
    """A safe, structured error response."""

    success: Literal[False] = False
    message: str
    error_code: str | None = None
    details: list[ErrorDetail] | None = None
