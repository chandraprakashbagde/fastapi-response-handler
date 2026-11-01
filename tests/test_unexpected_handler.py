import logging
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from fastapi_response_handler import register_handlers


class Number(BaseModel):
    number: int


def test_unexpected_and_internal_validation(caplog):
    app = FastAPI()
    register_handlers(app)
    @app.get("/unexpected")
    def unexpected():
        raise RuntimeError("private-secret")
    @app.get("/internal")
    def internal():
        return Number.model_validate({"number": "private-secret"})
    client = TestClient(app, raise_server_exceptions=False)
    with caplog.at_level(logging.ERROR, logger="fastapi_response_handler"):
        for path in ("/unexpected", "/internal"):
            response = client.get(path)
            assert response.status_code == 500
            assert response.json() == {"success": False, "message": "Internal server error", "error_code": "INTERNAL_SERVER_ERROR", "details": None}
            assert "private-secret" not in response.text
    assert len(caplog.records) == 2 and all(record.exc_info for record in caplog.records)
