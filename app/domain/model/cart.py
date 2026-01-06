from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.domain.exceptions import InvalidDomainException


class CartItem(BaseModel):
    """장바구니 항목 도메인 모델"""

    model_config = ConfigDict(from_attributes=True)

    id: Annotated[int | None, Field(title="고유 ID")] = None
    user_id: Annotated[int, Field(title="사용자 ID")]
    product_id: Annotated[int, Field(title="상품 ID")]
    quantity: Annotated[int, Field(gt=0, title="수량")]

    def add_quantity(self, amount: int) -> None:
        """수량을 증가시킵니다."""
        if amount <= 0:
            raise InvalidDomainException("추가할 수량은 0보다 커야 합니다.")
        self.quantity += amount

    def update_quantity(self, new_quantity: int) -> None:
        """수량을 변경합니다."""
        if new_quantity <= 0:
            raise InvalidDomainException("수량은 0보다 커야 합니다.")
        self.quantity = new_quantity
