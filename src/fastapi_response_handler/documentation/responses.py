"""Generate FastAPI response documentation."""
from http import HTTPStatus
from typing import Any, Iterable, Mapping

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from ..schemas import ErrorResponse

_DEFAULTS = (422, 500)


def _validate_status(code: int) -> None:
    if isinstance(code, bool) or not isinstance(code, int) or not 400 <= code <= 599:
        raise ValueError("response status codes must be integers between 400 and 599")


def api_responses(
    *status_codes: int,
    custom: Mapping[int, type[BaseModel]] | None = None,
    descriptions: Mapping[int, str] | None = None,
    exclude: Iterable[int] = (),
    examples: Mapping[int, Mapping[str, BaseModel | Mapping[str, Any]]] | None = None,
) -> dict[int, dict[str, Any]]:
    """Document errors, adding 422 and 500 by default unless excluded.

    Explicit status codes and custom models are included even if excluded from
    the defaults. Descriptions and named response-body examples may be
    supplied for included statuses. Examples document, but do not change,
    runtime responses; their values must be safe to publish.
    """
    custom = custom or {}
    descriptions = descriptions or {}
    examples = examples or {}
    excluded = set(exclude)
    for code in (*status_codes, *custom, *descriptions, *examples, *excluded):
        _validate_status(code)
    for model in custom.values():
        if not isinstance(model, type) or not issubclass(model, BaseModel):
            raise TypeError("custom response models must be Pydantic BaseModel subclasses")
    for description in descriptions.values():
        if not isinstance(description, str) or not description.strip():
            raise ValueError("descriptions must be non-empty strings")
    codes = dict.fromkeys((*[code for code in _DEFAULTS if code not in excluded], *status_codes, *custom))
    if set(descriptions) - codes.keys():
        raise ValueError("descriptions must refer to included responses")
    if set(examples) - codes.keys():
        raise ValueError("examples must refer to included responses")
    for named_examples in examples.values():
        if not isinstance(named_examples, Mapping) or not named_examples:
            raise ValueError("examples for each status must be a non-empty mapping")
        for name, value in named_examples.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError("example names must be non-empty strings")
            if not isinstance(value, (BaseModel, Mapping)):
                raise TypeError("example values must be Pydantic models or mappings")
    result: dict[int, dict[str, Any]] = {}
    for code in codes:
        try:
            description = HTTPStatus(code).phrase
        except ValueError:
            description = "Error response"
        result[code] = {"model": custom.get(code, ErrorResponse), "description": descriptions.get(code, description)}
        if code in examples:
            result[code]["content"] = {
                "application/json": {
                    "examples": {
                        name: {"value": jsonable_encoder(value)}
                        for name, value in examples[code].items()
                    }
                }
            }
    return result
