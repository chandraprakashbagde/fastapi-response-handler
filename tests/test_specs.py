"""Tests for single-source ErrorSpec and SuccessSpec definitions."""
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from fastapi_response_handler import (
    ConflictException,
    ErrorDetail,
    ErrorSpec,
    SuccessResponse,
    SuccessSpec,
    api_responses,
    error_response,
    register_handlers,
    success_response,
)

USER_NOT_FOUND = ErrorSpec("User not found", error_code="USER_NOT_FOUND", status_code=404)
INTERNAL_ERROR = ErrorSpec("Internal server error", error_code="INTERNAL_SERVER_ERROR")
AGE_DETAIL = ErrorDetail(field="body.age", message="Age must be greater than 18")
VALIDATION_INVALID_ID = ErrorSpec("Request validation failed", error_code="VALIDATION_ERROR", status_code=422, details=(AGE_DETAIL,))


def test_spec_response_matches_manual_envelope():
    assert USER_NOT_FOUND.response() == error_response("User not found", "USER_NOT_FOUND")
    assert INTERNAL_ERROR.response() == error_response("Internal server error", "INTERNAL_SERVER_ERROR")
    assert success_response(SuccessSpec("Done"), data=1) == success_response("Done", 1)
    assert SuccessSpec().response() == SuccessResponse()


def test_spec_with_details_and_clearing():
    assert VALIDATION_INVALID_ID.details == (AGE_DETAIL,)
    assert list(VALIDATION_INVALID_ID.response().details) == [AGE_DETAIL]
    cleared = VALIDATION_INVALID_ID.with_details()
    assert cleared.message == VALIDATION_INVALID_ID.message and cleared.details is None
    replaced = USER_NOT_FOUND.with_details(AGE_DETAIL)
    assert replaced.details == (AGE_DETAIL,) and USER_NOT_FOUND.details is None


def test_factories_accept_specs():
    assert error_response(USER_NOT_FOUND) == USER_NOT_FOUND.response()
    assert success_response(SuccessSpec("Created"), data="x") == success_response("Created", "x")


def test_from_spec_uses_spec_values():
    for spec, exc_type in ((USER_NOT_FOUND, ConflictException), (VALIDATION_INVALID_ID, ConflictException)):
        exception = exc_type.from_spec(spec)
        assert exception.message == spec.message
        assert exception.error_code == spec.error_code
        assert exception.status_code == spec.status_code
        assert exception.details == (list(spec.details) if spec.details is not None else None)


def test_endpoints_raise_and_respond_from_one_spec():
    app = FastAPI()
    register_handlers(app)

    @app.get("/items/{item_id}", responses=api_responses(404, examples={404: {"item_not_found": USER_NOT_FOUND}}))
    def read_item(item_id: int):
        raise ConflictException.from_spec(USER_NOT_FOUND)

    client = TestClient(app, raise_server_exceptions=False)
    body = client.get("/items/5").json()
    assert body == {"success": False, "message": "User not found", "error_code": "USER_NOT_FOUND", "details": None}
    documented = app.openapi()["paths"]["/items/{item_id}"]["get"]["responses"]["404"]["content"]["application/json"]["examples"]["item_not_found"]["value"]
    assert documented == {key: value for key, value in body.items() if value is not None}


def test_invalid_spec_examples_rejected():
    with __import__("pytest").raises(TypeError, match="example values"):
        api_responses(404, examples={404: {"bad": SuccessSpec("msg")}})


class PaymentError(BaseModel):
    reason: str


def test_spec_with_custom_model():
    spec = ErrorSpec("Declined", error_code="DECLINED", status_code=402)
    custom = error_response(spec, model=PaymentError, reason="no funds")
    assert custom.reason == "no funds" and not hasattr(custom, "error_code")
