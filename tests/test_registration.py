from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse
from fastapi_response_handler import ResponseHandlerConfig, register_handlers


def test_registration_and_override():
    app = FastAPI()
    async def override(request, exc):
        return JSONResponse({"override": True}, status_code=exc.status_code)
    register_handlers(app, ResponseHandlerConfig(), overrides={HTTPException: override})
    @app.get("/error")
    def error():
        raise HTTPException(403)
    response = TestClient(app).get("/error")
    assert response.status_code == 403 and response.json() == {"override": True}
