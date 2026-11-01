"""Reusable FastAPI response handling."""
from .schemas import ErrorDetail, ErrorSpec, ErrorResponse, SuccessResponse, SuccessSpec

__all__ = ["ErrorDetail", "ErrorSpec", "ErrorResponse", "SuccessResponse", "SuccessSpec"]
from .responses import error_response, http_response, success_response

__all__ += ["error_response", "http_response", "success_response"]
from .exceptions import APIException, BadRequestException, ConflictException, ForbiddenException, NotFoundException, UnauthorizedException

__all__ += ["APIException", "BadRequestException", "ConflictException", "ForbiddenException", "NotFoundException", "UnauthorizedException"]
from .config import ResponseHandlerConfig
from .registration import register_handlers

__all__ += ["ResponseHandlerConfig", "register_handlers"]
from .documentation import api_responses

__all__ += ["api_responses"]
