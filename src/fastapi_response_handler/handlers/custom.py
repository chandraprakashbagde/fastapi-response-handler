"""Application exception handling."""
from fastapi import Request
from starlette.responses import JSONResponse

from ..config import ResponseHandlerConfig
from ..exceptions import APIException
from ..responses import error_response, http_response


async def api_exception_handler(request: Request, exc: APIException, config: ResponseHandlerConfig | None = None) -> JSONResponse:
    """Return the deliberately public application exception payload."""
    config = config or ResponseHandlerConfig()
    return http_response(error_response(exc.message, exc.error_code, exc.details if config.include_error_details else None), exc.status_code)
