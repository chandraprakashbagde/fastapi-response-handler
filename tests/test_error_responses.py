from pydantic import BaseModel
from fastapi_response_handler import ErrorDetail, error_response, http_response


class CustomError(BaseModel):
    message: str
    trace: str


def test_error_and_http_response():
    error = error_response("Missing", "NOT_FOUND", [ErrorDetail(field="id", message="Missing")])
    assert error.model_dump()["details"][0]["field"] == "id"
    response = http_response(error, 404, {"X-Test": "yes"})
    assert response.status_code == 404 and response.headers["X-Test"] == "yes"


def test_custom_error():
    assert error_response("Oops", model=CustomError, trace="abc").trace == "abc"
