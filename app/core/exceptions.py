from typing import Any


class ExceptionCode:
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    BAD_REQUEST = "BAD_REQUEST"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"


class CustomException(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        data: Any | None = None,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.data = data
        super().__init__(self.message)
