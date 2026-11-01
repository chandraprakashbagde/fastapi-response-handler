"""Configuration for runtime exception handlers."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ResponseHandlerConfig:
    """Per-application settings. Messages supplied here must be safe to disclose."""

    include_error_details: bool = True
    validation_status_code: int = 422
    default_error_message: str = "Internal server error"
    log_unexpected_errors: bool = True

    def __post_init__(self) -> None:
        if not 400 <= self.validation_status_code <= 499:
            raise ValueError("validation_status_code must be a 4xx status")
        if not self.default_error_message:
            raise ValueError("default_error_message must not be empty")
