from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class CartItem(BaseModel):
    """장바구니 항목 도메인 모델"""

    model_config = ConfigDict(from_attributes=True)

    id: Annotated[int | None, Field(title="고유 ID")] = None
    user_id: Annotated[int, Field(title="사용자 ID")]
    product_id: Annotated[int, Field(title="상품 ID")]
    quantity: Annotated[int, Field(gt=0, title="수량")]
