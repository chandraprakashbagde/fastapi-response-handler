# Exception handling

```python
from fastapi import FastAPI
from fastapi_response_handler import APIException, register_handlers

app = FastAPI()
register_handlers(app)

class QuotaExceeded(APIException):
    default_status_code = 429
    default_message = "Quota exceeded"
    default_error_code = "QUOTA_EXCEEDED"

@app.get("/resource")
def resource():
    raise QuotaExceeded()
```

Starlette HTTP exceptions retain their status and headers. Request validation uses safe messages and dotted paths; internal Pydantic errors and other unexpected errors receive a generic 500. Exception and configured messages are application-controlled and must be safe to disclose. Avoid secrets in validation paths, custom exception messages, or custom details. Server logs contain the original exception and should be protected.

## Raising from named specs

Instead of repeating message strings at each raise site, define an `ErrorSpec` once and build the exception from it:

```python
from fastapi_response_handler import ErrorSpec, NotFoundException

USER_NOT_FOUND = ErrorSpec("User not found", error_code="USER_NOT_FOUND", status_code=404)

@app.get("/users/{user_id}")
def read_user(user_id: int):
    raise NotFoundException.from_spec(USER_NOT_FOUND)
```

The spec's values are authoritative: `status_code`, `error_code`, message, and details override the exception class defaults, so keep a spec's status consistent with the class you raise. The same spec can be passed to `error_response(SPEC)` and to `api_responses(..., examples={404: {"user_not_found": USER_NOT_FOUND}})`, keeping runtime exceptions, responses, and documentation in sync.
