import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi_response_handler import register_handlers


@pytest.mark.parametrize("status", [401, 403, 404])
def test_http_exceptions(status):
    app = FastAPI()
    register_handlers(app)
    @app.get("/exception")
    def endpoint():
        raise HTTPException(status, "Access denied", headers={"X-Reason": "example"})
    response = TestClient(app).get("/exception")
    assert response.status_code == status
    assert response.json() == {"success": False, "message": "Access denied", "error_code": f"HTTP_{status}", "details": None}
    assert response.headers["X-Reason"] == "example"


def test_starlette_routing_and_structured_and_server_errors():
    app = FastAPI()
    register_handlers(app)
    @app.get("/structured")
    def structured():
        raise StarletteHTTPException(400, {"token": "secret"})
    @app.get("/server")
    def server():
        raise HTTPException(500, "secret")
    client = TestClient(app)
    assert client.get("/missing").json()["error_code"] == "HTTP_404"
    assert "secret" not in client.get("/structured").text
    assert client.get("/server").json()["message"] == "Internal server error"
