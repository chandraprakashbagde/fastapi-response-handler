# Response handling

```python
from fastapi_response_handler import SuccessResponse, success_response, error_response, http_response

payload = success_response("Loaded", data=[{"id": 1}])
empty = SuccessResponse[dict](message="Done")
error = error_response("Unavailable", error_code="UNAVAILABLE")
http_error = http_response(error, status_code=503, headers={"Retry-After": "60"})
```

Normally return Pydantic models directly so FastAPI applies its `response_model` serialization. `http_response` explicitly serializes content and bypasses that route-level serialization. Native response types remain available.

## Named response specs

To keep each message in exactly one place, define `ErrorSpec` and `SuccessSpec` objects once (typically in a single module) and reuse them in services, endpoints, and OpenAPI examples:

```python
from fastapi_response_handler import ErrorDetail, ErrorSpec, SuccessSpec, error_response, success_response

USER_NOT_FOUND = ErrorSpec("User not found", error_code="USER_NOT_FOUND", status_code=404)
INVALID_USER_ID = ErrorSpec("Request validation failed", "VALIDATION_ERROR", status_code=422,
                            details=(ErrorDetail(field="path.user_id", message="Input should be a valid integer"),))
CREATED = SuccessSpec("User created successfully")

envelope = success_response(CREATED, data={"id": 1})
error = error_response(USER_NOT_FOUND)
variant = INVALID_USER_ID.with_details(ErrorDetail(field="body.age", message="Age must be greater than 18"))
```

`SPEC.with_details(*details)` derives a copy with different details; called without arguments it clears them. Specs are frozen dataclasses built once at import, so runtime construction cost is unchanged: one envelope validation per response, exactly as with literal arguments.
