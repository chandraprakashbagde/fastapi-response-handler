"""Success response construction."""
from typing import Any, TypeVar, overload

from pydantic import BaseModel

from ..schemas import SuccessResponse, SuccessSpec

M = TypeVar("M", bound=BaseModel)


@overload
def success_response(message: str | SuccessSpec = ..., data: Any = ..., *, model: None = ..., **fields: Any) -> SuccessResponse[Any]: ...


@overload
def success_response(message: str | SuccessSpec = ..., data: Any = ..., *, model: type[M], **fields: Any) -> M: ...


def success_response(message: str | SuccessSpec = "Operation completed successfully", data: Any = None, *, model: type[M] | None = None, **fields: Any) -> M | SuccessResponse[Any]:
    """Create a standard envelope from values or from a SuccessSpec, or validate fields with a custom model.

    For custom models, only declared envelope fields are supplied automatically;
    provide other required fields as keyword arguments.
    """
    cls = model or SuccessResponse[Any]
    values = {key: value for key, value in {"success": True, "message": message.message if isinstance(message, SuccessSpec) else message, "data": data}.items() if key in cls.model_fields}
    return cls.model_validate({**values, **fields})
