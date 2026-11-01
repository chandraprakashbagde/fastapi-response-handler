import asyncio
import json
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError
from starlette.exceptions import HTTPException
from fastapi_response_handler import APIException
from fastapi_response_handler.handlers import api_exception_handler, http_exception_handler, pydantic_validation_handler, request_validation_handler, unexpected_exception_handler


def run(handler, exc):
    return asyncio.run(handler(Request({"type": "http", "headers": []}), exc))


def test_handlers():
    response = run(request_validation_handler, RequestValidationError([{"loc": ("body", "items", 0, "name"), "type": "missing", "msg": "secret", "input": "secret"}]))
    assert json.loads(response.body)["details"] == [{"field": "body.items.0.name", "message": "Field required"}]
    response = run(http_exception_handler, HTTPException(403, "Access denied", {"X-Test": "1"}))
    assert response.status_code == 403 and response.headers["X-Test"] == "1"
    assert json.loads(response.body)["message"] == "Access denied"
    assert run(http_exception_handler, HTTPException(204)).body == b""
    assert json.loads(run(http_exception_handler, HTTPException(400, {"token": "secret"})).body)["message"] == "Bad Request"
    assert run(api_exception_handler, APIException("Missing", 404)).status_code == 404
    assert b"secret" not in run(unexpected_exception_handler, ValueError("secret")).body
    class Number(BaseModel):
        x: int
    try:
        Number(x="secret")
    except ValidationError as exc:
        assert b"secret" not in run(pydantic_validation_handler, exc).body
