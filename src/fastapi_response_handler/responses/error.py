"""Error response construction and explicit HTTP serialization."""
from typing import Any, Mapping, TypeVar, overload

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from starlette.responses import JSONResponse

from ..schemas import ErrorDetail, ErrorResponse

M = TypeVar("M", bound=BaseModel)


@overload
def error_response(message: str, error_code: str | None = ..., details: list[ErrorDetail] | None = ..., *, model: None = ..., **fields: Any) -> ErrorResponse: ...


@overload
def error_response(message: str, error_code: str | None = ..., details: list[ErrorDetail] | None = ..., *, model: type[M], **fields: Any) -> M: ...


def error_response(message: str, error_code: str | None = None, details: list[ErrorDetail] | None = None, *, model: type[M] | None = None, **fields: Any) -> M | ErrorResponse:
    """Create an error envelope or a compatible custom Pydantic model."""
    cls = model or ErrorResponse
    values = {key: value for key, value in {"success": False, "message": message, "error_code": error_code, "details": details}.items() if key in cls.model_fields}
    return cls.model_validate({**values, **fields})


def http_response(content: BaseModel | Any, status_code: int = 200, headers: Mapping[str, str] | None = None) -> JSONResponse:
    """Serialize content explicitly as a JSON response with status and headers."""
    return JSONResponse(content=jsonable_encoder(content), status_code=status_code, headers=dict(headers) if headers else None)
