import pytest
from fastapi_response_handler import APIException, BadRequestException, ConflictException, ForbiddenException, NotFoundException, UnauthorizedException


def test_specialized_exceptions():
    for cls, status in [(BadRequestException, 400), (UnauthorizedException, 401), (ForbiddenException, 403), (NotFoundException, 404), (ConflictException, 409)]:
        assert cls().status_code == status
    assert NotFoundException("Missing", error_code="USER_NOT_FOUND").error_code == "USER_NOT_FOUND"


def test_invalid_status():
    with pytest.raises(ValueError):
        APIException(status_code=200)
