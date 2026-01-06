from pydantic import BaseModel, ConfigDict, Field

from app.domain.exceptions import (
    InsufficientStockException,
    InvalidDomainException,
    PermissionDeniedException,
)


class Product(BaseModel):
    """상품 도메인 모델"""

    id: int | None = Field(default=None, title="고유 ID", description="상품의 고유 식별자")
    name: str = Field(title="상품명", description="상품의 이름")
    description: str | None = Field(default=None, title="상품 설명", description="상품에 대한 상세 설명")
    price: float = Field(gt=0, title="가격", description="상품의 가격. 0보다 커야 합니다.")
    stock: int = Field(ge=0, title="재고 수량", description="남아있는 상품의 수량. 0 이상이어야 합니다.")
    seller_id: int = Field(title="판매자 ID", description="상품을 등록한 판매자의 고유 ID")
    version: int = Field(default=1, title="버전", description="낙관적 락을 위한 버전 정보")

    model_config = ConfigDict(from_attributes=True)

    def decrease_stock(self, quantity: int) -> None:
        """재고를 차감합니다."""
        if quantity <= 0:
            raise InvalidDomainException("차감할 수량은 0보다 커야 합니다.")

        self.check_stock(quantity)

        self.stock -= quantity

    def check_stock(self, quantity: int) -> None:
        """재고가 충분한지 확인합니다."""
        if self.stock < quantity:
            raise InsufficientStockException(f"재고가 부족합니다. (현재: {self.stock}, 요청: {quantity})")

    def verify_owner(self, seller_id: int) -> None:
        """상품의 소유자인지 확인합니다."""
        if self.seller_id != seller_id:
            raise PermissionDeniedException("해당 상품에 대한 권한이 없습니다.")

    def update_price(self, new_price: float) -> None:
        """가격을 변경합니다."""
        if new_price <= 0:
            raise InvalidDomainException("가격은 0보다 커야 합니다.")
        self.price = new_price

    def add_stock(self, quantity: int) -> None:
        """재고를 추가합니다."""
        if quantity <= 0:
            raise InvalidDomainException("추가할 수량은 0보다 커야 합니다.")
        self.stock += quantity

    def update_details(
        self,
        name: str | None = None,
        description: str | None = None,
        price: float | None = None,
        stock: int | None = None,
    ) -> None:
        """
        상품 정보를 수정합니다.
        값이 제공된 필드만 수정됩니다.
        """
        if name is not None:
            self.name = name

        if description is not None:
            self.description = description

        if price is not None:
            self.update_price(price)

        if stock is not None:
            if stock < 0:
                raise InvalidDomainException("재고는 0보다 적을 수 없습니다.")
            self.stock = stock
