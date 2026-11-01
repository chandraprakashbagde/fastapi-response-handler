import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_response_handler import APIException, BadRequestException, ConflictException, ErrorDetail, ForbiddenException, NotFoundException, UnauthorizedException, register_handlers


class InventoryError(APIException):
    default_status_code = 409
    default_error_code = "OUT_OF_STOCK"


def test_subclass():
    app = FastAPI()
    register_handlers(app)
    @app.get("/")
    def endpoint():
        raise InventoryError("Unavailable", details=[ErrorDetail(field="sku", message="Sold out")])
    response = TestClient(app).get("/")
    assert response.status_code == 409
    assert response.json() == {"success": False, "message": "Unavailable", "error_code": "OUT_OF_STOCK", "details": [{"field": "sku", "message": "Sold out"}]}


@pytest.mark.parametrize("cls,status", [(NotFoundException, 404), (UnauthorizedException, 401), (ForbiddenException, 403), (ConflictException, 409), (BadRequestException, 400)])
def test_specialized_http(cls, status):
    app = FastAPI()
    register_handlers(app)
    @app.get("/")
    def endpoint():
        raise cls()
    response = TestClient(app).get("/")
    assert response.status_code == status and response.json()["success"] is False
