"""Application exception hierarchy."""
from ..schemas import ErrorDetail, ErrorSpec


class APIException(Exception):
    """A deliberately client-facing application error.

    Messages and details must be safe to disclose to callers.
    """

    default_status_code = 500
    default_message = "Internal server error"
    default_error_code: str | None = None

    def __init__(self, message: str | None = None, status_code: int | None = None, error_code: str | None = None, details: list[ErrorDetail] | None = None) -> None:
        self.message = message if message is not None else self.default_message
        self.status_code = status_code if status_code is not None else self.default_status_code
        if not 400 <= self.status_code <= 599:
            raise ValueError("APIException status_code must be between 400 and 599")
        self.error_code = error_code if error_code is not None else self.default_error_code
        self.details = details
        super().__init__(self.message)

    @classmethod
    def from_spec(cls, spec: ErrorSpec) -> "APIException":
        """Build this exception from an ErrorSpec; the spec's values are authoritative."""
        return cls(spec.message, status_code=spec.status_code, error_code=spec.error_code, details=list(spec.details) if spec.details is not None else None)


class NotFoundException(APIException):
    """A requested resource does not exist."""
    default_status_code = 404
    default_message = "Not found"
    default_error_code = "NOT_FOUND"


class UnauthorizedException(APIException):
    """Authentication is required or failed."""
    default_status_code = 401
    default_message = "Unauthorized"
    default_error_code = "UNAUTHORIZED"


class ForbiddenException(APIException):
    """The caller is not permitted to perform the operation."""
    default_status_code = 403
    default_message = "Forbidden"
    default_error_code = "FORBIDDEN"


class ConflictException(APIException):
    """The requested operation conflicts with current state."""
    default_status_code = 409
    default_message = "Conflict"
    default_error_code = "CONFLICT"


class BadRequestException(APIException):
    """The client submitted an invalid request."""
    default_status_code = 400
    default_message = "Bad request"
    default_error_code = "BAD_REQUEST"
