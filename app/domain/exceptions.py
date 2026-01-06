class DomainException(Exception):
    """도메인 계층의 기본 예외 클래스"""

    pass


class InvalidDomainException(DomainException):
    """도메인 규칙 위반 또는 유효하지 않은 상태 예외"""

    pass


class InsufficientStockException(DomainException):
    """재고 부족 예외"""

    pass
