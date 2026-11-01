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
