"""Generic success envelope."""
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """A success message with an optional typed payload."""

    success: Literal[True] = True
    message: str = "Operation completed successfully"
    data: T | None = None
