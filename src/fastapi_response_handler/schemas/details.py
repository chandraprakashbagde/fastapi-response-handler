"""Public error detail model."""
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """A client-facing error associated with a field or path."""

    field: str
    message: str
