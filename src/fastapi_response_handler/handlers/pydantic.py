"""Internal Pydantic validation handling."""
from fastapi import Request
from pydantic import ValidationError
from starlette.responses import JSONResponse

from ..config import ResponseHandlerConfig
from .unexpected import unexpected_exception_handler


async def pydantic_validation_handler(request: Request, exc: ValidationError, config: ResponseHandlerConfig | None = None) -> JSONResponse:
    """Treat internal model validation failures as server errors, not client errors."""
    return await unexpected_exception_handler(request, exc, config)
