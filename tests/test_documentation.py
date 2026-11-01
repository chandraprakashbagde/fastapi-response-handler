import pytest
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi_response_handler import ErrorResponse, api_responses


class PaymentError(BaseModel):
    reason: str


def test_openapi():
    app = FastAPI()
    @app.get("/pay", responses=api_responses(400, custom={402: PaymentError}, descriptions={402: "Payment declined"}, exclude={500}))
    def pay():
        return {}
    responses = app.openapi()["paths"]["/pay"]["get"]["responses"]
    assert responses["400"]["content"]["application/json"]["schema"]["$ref"].endswith("/ErrorResponse")
    assert responses["402"]["content"]["application/json"]["schema"]["$ref"].endswith("/PaymentError")
    assert responses["402"]["description"] == "Payment declined"
    assert "500" not in responses and "422" in responses
    assert api_responses(500, exclude={500})[500]["model"] is ErrorResponse


def test_invalid_options():
    for code in (200, 600, True):
        with pytest.raises(ValueError):
            api_responses(code)
    with pytest.raises(TypeError):
        api_responses(custom={400: dict})
    with pytest.raises(ValueError):
        api_responses(descriptions={400: "Unused"})


def test_named_examples_in_openapi():
    from fastapi_response_handler import ErrorDetail, error_response

    app = FastAPI()
    @app.post("/users", responses=api_responses(
        409,
        examples={
            409: {"duplicate_email": error_response("User with this email already exists", "USER_EMAIL_EXISTS")},
            422: {
                "age": error_response("Request validation failed", "VALIDATION_ERROR", [ErrorDetail(field="body.age", message="Age must be greater than 18")]),
                "password": {"success": False, "message": "Request validation failed", "error_code": "VALIDATION_ERROR", "details": [{"field": "body", "message": "password and confirm password should match"}]},
            },
        },
    ))
    def create_user():
        return {}

    responses = app.openapi()["paths"]["/users"]["post"]["responses"]
    content = responses["422"]["content"]["application/json"]
    assert content["schema"]["$ref"].endswith("/ErrorResponse")
    assert set(content["examples"]) == {"age", "password"}
    assert content["examples"]["age"]["value"]["details"][0]["message"] == "Age must be greater than 18"
    assert responses["409"]["content"]["application/json"]["examples"]["duplicate_email"]["value"]["error_code"] == "USER_EMAIL_EXISTS"


def test_invalid_examples():
    with pytest.raises(ValueError, match="included responses"):
        api_responses(examples={409: {"error": {}}})
    with pytest.raises(ValueError, match="non-empty mapping"):
        api_responses(409, examples={409: {}})
    with pytest.raises(ValueError, match="names"):
        api_responses(409, examples={409: {"": {}}})
    with pytest.raises(TypeError, match="example values"):
        api_responses(409, examples={409: {"error": "bad"}})


def test_examples_with_custom_error_model():
    app = FastAPI()
    @app.get("/payment", responses=api_responses(custom={402: PaymentError}, examples={402: {"declined": PaymentError(reason="declined")}}))
    def payment():
        return {}
    content = app.openapi()["paths"]["/payment"]["get"]["responses"]["402"]["content"]["application/json"]
    assert content["schema"]["$ref"].endswith("/PaymentError")
    assert content["examples"]["declined"]["value"] == {"reason": "declined"}
