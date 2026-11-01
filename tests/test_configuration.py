import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from fastapi_response_handler import APIException, ErrorDetail, ResponseHandlerConfig, register_handlers


class Payload(BaseModel):
    value: int


def test_configuration_applies_per_app():
    app = FastAPI()
    register_handlers(app, ResponseHandlerConfig(include_error_details=False, validation_status_code=400, default_error_message="Something went wrong", log_unexpected_errors=False))
    @app.post("/validate")
    def validate(payload: Payload):
        return payload
    @app.get("/custom")
    def custom():
        raise APIException("Invalid", 400, details=[ErrorDetail(field="x", message="wrong")])
    @app.get("/unexpected")
    def unexpected():
        raise ValueError("sensitive")
    client = TestClient(app, raise_server_exceptions=False)
    validation = client.post("/validate", json={})
    assert validation.status_code == 400 and validation.json()["details"] is None
    assert client.get("/custom").json()["details"] is None
    assert client.get("/unexpected").json()["message"] == "Something went wrong"


def test_invalid_configuration():
    with pytest.raises(ValueError):
        ResponseHandlerConfig(validation_status_code=500)
    with pytest.raises(ValueError):
        ResponseHandlerConfig(default_error_message="")
