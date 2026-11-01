"""Request validation handling without rejected values."""
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from ..config import ResponseHandlerConfig
from ..responses import error_response, http_response
from ..schemas import ErrorDetail

_MESSAGES = {
    "missing": "Field required",
    "string_type": "Input should be a valid string",
    "int_parsing": "Input should be a valid integer",
    "int_type": "Input should be a valid integer",
    "float_parsing": "Input should be a valid number",
    "list_type": "Input should be a valid list",
    "dict_type": "Input should be a valid dictionary",
    "json_invalid": "Invalid JSON",
}


async def request_validation_handler(request: Request, exc: RequestValidationError, config: ResponseHandlerConfig | None = None) -> JSONResponse:
    """Return safe field paths and fixed messages for invalid requests."""
    config = config or ResponseHandlerConfig()
    details = None
    if config.include_error_details:
        details = [ErrorDetail(field=".".join(str(part) for part in error.get("loc", ())), message=_MESSAGES.get(error.get("type"), "Invalid value")) for error in exc.errors()]
    return http_response(error_response("Request validation failed", "VALIDATION_ERROR", details), config.validation_status_code)
