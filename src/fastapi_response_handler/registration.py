"""Install exception handlers on a FastAPI application."""
from functools import partial
from typing import Any, Callable, Mapping

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException

from .config import ResponseHandlerConfig
from .exceptions import APIException
from .handlers import api_exception_handler, http_exception_handler, pydantic_validation_handler, request_validation_handler, unexpected_exception_handler


def register_handlers(app: FastAPI, config: ResponseHandlerConfig | None = None, *, overrides: Mapping[type[Exception] | int, Callable[..., Any]] | None = None) -> None:
    """Register handlers before the app starts; overrides use Starlette's handler signature.

    Existing handlers for these keys are replaced. Starlette middleware is built
    on first use, so registering after startup is not supported.
    """
    config = config or ResponseHandlerConfig()
    handlers = {
        RequestValidationError: request_validation_handler,
        ValidationError: pydantic_validation_handler,
        HTTPException: http_exception_handler,
        APIException: api_exception_handler,
        Exception: unexpected_exception_handler,
    }
    for exc_type, handler in handlers.items():
        app.add_exception_handler(exc_type, partial(handler, config=config))
    for exc_type, handler in (overrides or {}).items():
        app.add_exception_handler(exc_type, handler)
