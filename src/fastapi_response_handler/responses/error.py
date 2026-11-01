"""Error response construction and explicit HTTP serialization."""
from typing import Any, Mapping, TypeVar, overload

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from starlette.responses import JSONResponse

from ..schemas import ErrorDetail, ErrorSpec, ErrorResponse

M = TypeVar("M", bound=BaseModel)


@overload
def error_response(message: str, error_code: str | None = ..., details: list[ErrorDetail] | None = ..., *, model: None = ..., **fields: Any) -> ErrorResponse: ...


@overload
def error_response(message: ErrorSpec, *, model: None = ..., **fields: Any) -> ErrorResponse: ...


@overload
def error_response(message: str, error_code: str | None = ..., details: list[ErrorDetail] | None = ..., *, model: type[M], **fields: Any) -> M: ...


@overload
def error_response(message: ErrorSpec, *, model: type[M], **fields: Any) -> M: ...


def error_response(message: str | ErrorSpec, error_code: str | None = None, details: list[ErrorDetail] | None = None, *, model: type[M] | None = None, **fields: Any) -> M | ErrorResponse:
    """Create an error envelope from values or from an ErrorSpec, or a compatible custom Pydantic model."""
    if isinstance(message, ErrorSpec):
        values: dict[str, Any] = {"message": message.message, "error_code": message.error_code, "details": message.details}
    else:
        values = {"message": message, "error_code": error_code, "details": details}
    cls = model or ErrorResponse
    values = {key: value for key, value in {"success": False, **values}.items() if key in cls.model_fields}
    return cls.model_validate({**values, **fields})


def http_response(content: BaseModel | Any, status_code: int = 200, headers: Mapping[str, str] | None = None) -> JSONResponse:
    """Serialize content explicitly as a JSON response with status and headers."""
    return JSONResponse(content=jsonable_encoder(content), status_code=status_code, headers=dict(headers) if headers else None)
