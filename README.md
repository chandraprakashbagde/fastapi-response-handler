# fastapi-response-handler

Reusable Pydantic v2 response envelopes, FastAPI exception handlers, and OpenAPI response definitions for Python 3.10+. Independent of application domain and storage.

## Features

- Typed success and error schemas, plus opt-in response factories and an HTTP JSON utility.
- Centralized handling for request validation, internal Pydantic validation, Starlette/FastAPI HTTP errors, application exceptions, and unexpected failures.
- Configurable status, error details, logging and error message; handler overrides.
- Per-endpoint OpenAPI response documentation with custom models and descriptions.
- Native FastAPI responses and custom models remain usable without an envelope.

## Installation

After publication, install with `pip install fastapi-response-handler`. This source project is not automatically published. To install locally:

```bash
cd fastapi-response-handler
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
python -m build
```

For step-by-step instructions on using the local package in other FastAPI projects, see the [local installation guide](docs/installation.html).

For the example server, install Uvicorn separately (`pip install uvicorn`) and run `uvicorn examples.basic_app:app --reload`.

## Complete application

```python
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi_response_handler import (
    NotFoundException, ResponseHandlerConfig, SuccessResponse,
    api_responses, register_handlers, success_response,
)

app = FastAPI()
register_handlers(app, ResponseHandlerConfig())

class User(BaseModel):
    id: int
    name: str

@app.get("/users/{user_id}", response_model=SuccessResponse[User],
         responses=api_responses(404))
def get_user(user_id: int):
    if user_id != 1:
        raise NotFoundException("User not found", error_code="USER_NOT_FOUND")
    return success_response("User found", User(id=1, name="Ada"))
```

`success_response(data=user)` returns a Pydantic model, not an HTTP response. Omit data for `null`; use `SuccessResponse[list[User]]`, `SuccessResponse[dict]`, etc. as response models. FastAPI performs its usual validation and serialization.

## Error responses and exceptions

```python
from fastapi_response_handler import APIException, ErrorDetail, error_response, http_response

error = error_response("User not found", "USER_NOT_FOUND", [
    ErrorDetail(field="id", message="No user with this ID")
])
response = http_response(error, status_code=404, headers={"X-Reason": "missing"})
raise APIException("User not found", status_code=404, error_code="USER_NOT_FOUND")
```

Built-in subclasses: `NotFoundException`, `UnauthorizedException`, `ForbiddenException`, `ConflictException`, `BadRequestException`. Subclass `APIException` and set `default_status_code`, `default_message` and `default_error_code` to define your own. Exception messages and details are **public**; do not include secrets. Register handlers before the first request. Registering replaces existing handlers for those exception types; use `overrides={ExceptionType: handler}` to supply standard `(request, exc)` handlers.

## OpenAPI

```python
from pydantic import BaseModel
from fastapi_response_handler import api_responses

class PaymentError(BaseModel):
    reason: str

responses = api_responses(400, 401, custom={402: PaymentError},
                          descriptions={402: "Payment declined"}, exclude={500})
```

Pass this dictionary to an endpoint's `responses=`. It documents responses only; it does not produce or validate runtime errors. By default 422 and 500 are documented; `exclude` removes defaults only, and explicitly requested codes/custom models are included. Codes must be 4xx or 5xx. If changing `validation_status_code`, explicitly document that code and exclude 422 if appropriate. FastAPI can independently add its own 422 documentation for endpoints with request parameters.

Add named examples to show actual error bodies and messages in Swagger's response examples dropdown:

```python
from fastapi_response_handler import ErrorDetail, api_responses, error_response

responses = api_responses(
    409,
    examples={
        409: {"email_exists": error_response("User with this email already exists", "USER_EMAIL_EXISTS")},
        422: {"age": error_response("Request validation failed", "VALIDATION_ERROR", [
            ErrorDetail(field="body.age", message="Age must be greater than 18")
        ])},
    },
)
```

Each status maps example names to Pydantic models or JSON-compatible response-body mappings; custom response models are supported. An example status must already be included explicitly, via `custom`, or by default. Examples are illustrative and are not checked against runtime behavior or schemas: maintain them alongside handlers, use safe public values, and document only errors the endpoint can actually return. FastAPI's OpenAPI serialization can omit `null` fields from examples even when the runtime response includes them.

## Custom models and native responses

```python
from pydantic import BaseModel
from fastapi_response_handler import success_response, error_response

class PaymentResponse(BaseModel):
    success: bool
    transaction_id: str
    payment_status: str

payment = success_response(model=PaymentResponse, transaction_id="t1", payment_status="paid")

class CustomError(BaseModel):
    message: str
    reference: str

error = error_response("Declined", model=CustomError, reference="r1")
```

Factories supply envelope fields only when they are declared by the custom model; supply other fields as keywords. A custom documented error model does not change handler output: use `overrides` or an application handler to actually return it. Endpoints can alternatively return any Pydantic model, `JSONResponse`, `FileResponse`, `StreamingResponse`, or redirects directly.

## Configuration and security

| `ResponseHandlerConfig` option | Default | Meaning |
| --- | --- | --- |
| `include_error_details` | `True` | Include request validation and application exception details |
| `validation_status_code` | `422` | Status for request validation (4xx only) |
| `default_error_message` | `Internal server error` | Public message for internal and HTTP 5xx errors |
| `log_unexpected_errors` | `True` | Log unexpected and internal Pydantic exceptions with tracebacks |

Request validation returns dotted locations and safe fixed messages, never Pydantic input/context or arbitrary validator messages. Dictionary keys in paths may themselves be user-supplied; disable details if these could contain sensitive data. HTTP 4xx string details are treated as intentionally public; structured details are redacted, and 5xx details are replaced with the configured generic message. No setting exposes internal exception messages or stack traces in responses. Logs contain original exception details and must be protected/redacted according to your policy. If middleware sets `request.state.request_id`, it is included in logs; the package does not trust or create an ID from request headers.

Internal Pydantic validation failures are 500s, not automatically 422s. Explicitly catch and translate errors into a safe `APIException` if the application knows they are client errors. Set `debug=False` in production: Starlette debug mode can expose traceback responses. Starlette server-error handling re-raises exceptions after sending a response; tests inspecting 500 bodies should use `TestClient(app, raise_server_exceptions=False)`. Exceptions after streaming has started cannot be replaced with a JSON envelope.

Open the [HTML documentation](docs/index.html) for a responsive guide, or see the Markdown guides: [getting started](docs/getting_started.md), [responses](docs/response_handling.md), [exceptions](docs/exception_handling.md), [customization](docs/customization.md).
