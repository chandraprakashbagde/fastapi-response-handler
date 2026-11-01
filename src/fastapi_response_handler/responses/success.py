"""Success response construction."""
from typing import Any, TypeVar, overload

from pydantic import BaseModel

from ..schemas import SuccessResponse

M = TypeVar("M", bound=BaseModel)


@overload
def success_response(message: str = ..., data: Any = ..., *, model: None = ..., **fields: Any) -> SuccessResponse[Any]: ...


@overload
def success_response(message: str = ..., data: Any = ..., *, model: type[M], **fields: Any) -> M: ...


def success_response(message: str = "Operation completed successfully", data: Any = None, *, model: type[M] | None = None, **fields: Any) -> M | SuccessResponse[Any]:
    """Create a standard envelope, or validate fields with a custom model.

    For custom models, only declared envelope fields are supplied automatically;
    provide other required fields as keyword arguments.
    """
    cls = model or SuccessResponse[Any]
    values = {key: value for key, value in {"success": True, "message": message, "data": data}.items() if key in cls.model_fields}
    return cls.model_validate({**values, **fields})
