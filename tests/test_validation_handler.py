from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, field_validator
from fastapi_response_handler import register_handlers


class Item(BaseModel):
    email: str
    count: int

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError(f"bad email: {value}")
        return value


class Payload(BaseModel):
    items: list[Item]
    lookup: dict[str, int]


def test_nested_missing_invalid_email_and_dict():
    app = FastAPI()
    register_handlers(app)
    @app.post("/items")
    def create(payload: Payload):
        return payload
    client = TestClient(app)
    response = client.post("/items", json={"items": [{"email": "secret-invalid"}], "lookup": {"first": "not-a-number"}})
    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "VALIDATION_ERROR"
    assert {item["field"] for item in body["details"]} == {"body.items.0.email", "body.items.0.count", "body.lookup.first"}
    assert "secret-invalid" not in response.text and "not-a-number" not in response.text
    assert any(item["message"] == "Field required" for item in body["details"])
