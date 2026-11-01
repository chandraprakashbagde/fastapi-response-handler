# Response handling

```python
from fastapi_response_handler import SuccessResponse, success_response, error_response, http_response

payload = success_response("Loaded", data=[{"id": 1}])
empty = SuccessResponse[dict](message="Done")
error = error_response("Unavailable", error_code="UNAVAILABLE")
http_error = http_response(error, status_code=503, headers={"Retry-After": "60"})
```

Normally return Pydantic models directly so FastAPI applies its `response_model` serialization. `http_response` explicitly serializes content and bypasses that route-level serialization. Native response types remain available.
