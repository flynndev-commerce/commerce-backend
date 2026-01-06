from typing import Any

from starlette import status


class ExceptionCode:
    INTERNAL_SERVER_ERROR: str = "INTERNAL_SERVER_ERROR"
    BAD_REQUEST: str = "BAD_REQUEST"
    VALIDATION_ERROR: str = "VALIDATION_ERROR"
    NOT_FOUND: str = "NOT_FOUND"
    UNAUTHORIZED: str = "UNAUTHORIZED"
    FORBIDDEN: str = "FORBIDDEN"

    # User
    USER_NOT_FOUND: str = "USER_NOT_FOUND"
    EMAIL_ALREADY_EXISTS: str = "EMAIL_ALREADY_EXISTS"
    INVALID_PASSWORD: str = "INVALID_PASSWORD"
    USER_INACTIVE: str = "USER_INACTIVE"

    # Product
    PRODUCT_NOT_FOUND: str = "PRODUCT_NOT_FOUND"
    INSUFFICIENT_STOCK: str = "INSUFFICIENT_STOCK"
    CONCURRENT_MODIFICATION: str = "CONCURRENT_MODIFICATION"

    # Cart
    CART_ITEM_NOT_FOUND: str = "CART_ITEM_NOT_FOUND"

    # Order
    ORDER_NOT_FOUND: str = "ORDER_NOT_FOUND"
    EMPTY_CART: str = "EMPTY_CART"

    # Seller
    SELLER_ALREADY_EXISTS: str = "SELLER_ALREADY_EXISTS"


class CustomException(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        data: Any | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.data = data
        super().__init__(self.message)


class NotFoundException(CustomException):
    def __init__(self, code: str = ExceptionCode.NOT_FOUND, message: str = "Not Found") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, code=code, message=message)


class BadRequestException(CustomException):
    def __init__(self, code: str = ExceptionCode.BAD_REQUEST, message: str = "Bad Request") -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, code=code, message=message)


class UnauthorizedException(CustomException):
    def __init__(self, code: str = ExceptionCode.UNAUTHORIZED, message: str = "Unauthorized") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, code=code, message=message)


class InvalidCredentialsException(UnauthorizedException):
    def __init__(self) -> None:
        super().__init__(message="이메일 또는 비밀번호가 올바르지 않습니다.")


class ForbiddenException(CustomException):
    def __init__(self, code: str = ExceptionCode.FORBIDDEN, message: str = "Forbidden") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, code=code, message=message)


# Domain Exceptions


class UserNotFoundException(NotFoundException):
    def __init__(self, message: str = "사용자를 찾을 수 없습니다.") -> None:
        super().__init__(code=ExceptionCode.USER_NOT_FOUND, message=message)


class EmailAlreadyExistsException(BadRequestException):
    def __init__(self, message: str = "이미 존재하는 이메일입니다.") -> None:
        super().__init__(code=ExceptionCode.EMAIL_ALREADY_EXISTS, message=message)


class InvalidPasswordException(BadRequestException):
    def __init__(self, message: str = "비밀번호가 일치하지 않습니다.") -> None:
        super().__init__(code=ExceptionCode.INVALID_PASSWORD, message=message)


class UserInactiveException(BadRequestException):
    def __init__(self, message: str = "비활성화된 계정입니다.") -> None:
        super().__init__(code=ExceptionCode.USER_INACTIVE, message=message)


class ProductNotFoundException(NotFoundException):
    def __init__(self, message: str = "상품을 찾을 수 없습니다.") -> None:
        super().__init__(code=ExceptionCode.PRODUCT_NOT_FOUND, message=message)


class InsufficientStockException(CustomException):
    def __init__(self, message: str = "재고가 부족합니다.") -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            code=ExceptionCode.INSUFFICIENT_STOCK,
            message=message,
        )


class CartItemNotFoundException(NotFoundException):
    def __init__(self, message: str = "장바구니 아이템을 찾을 수 없습니다.") -> None:
        super().__init__(code=ExceptionCode.CART_ITEM_NOT_FOUND, message=message)


class OrderNotFoundException(NotFoundException):
    def __init__(self, message: str = "주문을 찾을 수 없습니다.") -> None:
        super().__init__(code=ExceptionCode.ORDER_NOT_FOUND, message=message)


class EmptyCartException(BadRequestException):
    def __init__(self, message: str = "장바구니가 비어있습니다.") -> None:
        super().__init__(code=ExceptionCode.EMPTY_CART, message=message)


class SellerAlreadyExistsException(BadRequestException):
    def __init__(self, message: str = "이미 판매자로 등록된 사용자입니다.") -> None:
        super().__init__(code=ExceptionCode.SELLER_ALREADY_EXISTS, message=message)
