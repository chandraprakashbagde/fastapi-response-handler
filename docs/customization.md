# Customization

```python
from fastapi import FastAPI
from starlette.responses import JSONResponse
from fastapi_response_handler import ResponseHandlerConfig, APIException, register_handlers

app = FastAPI()

async def custom_api_error(request, exc):
    return JSONResponse({"reason": exc.message}, status_code=exc.status_code)

register_handlers(app, ResponseHandlerConfig(include_error_details=False),
                  overrides={APIException: custom_api_error})
```

Overrides are ordinary Starlette exception handlers and are responsible for their own serialization and safety. Use `api_responses(custom={409: YourErrorModel})` to document an application-specific error; it does not change the handler. Custom success models may be returned directly or constructed with `success_response(model=YourModel, ...)`.
