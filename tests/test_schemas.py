from pydantic import BaseModel
from fastapi_response_handler import ErrorDetail, ErrorResponse, SuccessResponse


class User(BaseModel):
    name: str


def test_generic_schema():
    response = SuccessResponse[list[User]](data=[User(name="Ada")])
    assert response.model_dump() == {"success": True, "message": "Operation completed successfully", "data": [{"name": "Ada"}]}
    assert SuccessResponse[dict]().data is None


def test_error_schema():
    assert ErrorResponse(message="Invalid", details=[ErrorDetail(field="body.email", message="Invalid")]).model_dump()["success"] is False
