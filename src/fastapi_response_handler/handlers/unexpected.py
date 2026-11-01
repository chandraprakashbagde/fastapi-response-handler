"""Safe handling of unexpected failures."""
import logging

from fastapi import Request
from starlette.responses import JSONResponse

from ..config import ResponseHandlerConfig
from ..responses import error_response, http_response

logger = logging.getLogger("fastapi_response_handler")


async def unexpected_exception_handler(request: Request, exc: Exception, config: ResponseHandlerConfig | None = None) -> JSONResponse:
    """Log the exception and return a generic response without a traceback."""
    config = config or ResponseHandlerConfig()
    if config.log_unexpected_errors:
        logger.error("Unhandled exception (request_id=%s)", getattr(request.state, "request_id", None), exc_info=(type(exc), exc, exc.__traceback__))
    return http_response(error_response(config.default_error_message, "INTERNAL_SERVER_ERROR"), 500)
