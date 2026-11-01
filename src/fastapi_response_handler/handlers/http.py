"""Starlette HTTP exception handling."""
from http import HTTPStatus

from fastapi import Request
from fastapi.utils import is_body_allowed_for_status_code
from starlette.exceptions import HTTPException
from starlette.responses import Response

from ..config import ResponseHandlerConfig
from ..responses import error_response, http_response


async def http_exception_handler(request: Request, exc: HTTPException, config: ResponseHandlerConfig | None = None) -> Response:
    """Preserve status and headers; structured details and 5xx details are redacted."""
    config = config or ResponseHandlerConfig()
    if not is_body_allowed_for_status_code(exc.status_code):
        return Response(status_code=exc.status_code, headers=exc.headers)
    if exc.status_code >= 500:
        message = config.default_error_message
    elif isinstance(exc.detail, str):
        message = exc.detail
    else:
        try:
            message = HTTPStatus(exc.status_code).phrase
        except ValueError:
            message = "HTTP error"
    return http_response(error_response(message, f"HTTP_{exc.status_code}"), exc.status_code, exc.headers)
