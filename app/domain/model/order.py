from datetime import datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class OrderStatus(StrEnum):
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class OrderItem(BaseModel):
    """주문 항목 도메인 모델"""

    model_config = ConfigDict(from_attributes=True)

    id: Annotated[int | None, Field(title="고유 ID")] = None
    product_id: Annotated[int, Field(title="상품 ID")]
    price: Annotated[float, Field(gt=0, title="주문 당시 가격")]
    quantity: Annotated[int, Field(gt=0, title="주문 수량")]


class Order(BaseModel):
    """주문 도메인 모델"""

    model_config = ConfigDict(from_attributes=True)

    id: Annotated[int | None, Field(title="고유 ID")] = None
    user_id: Annotated[int, Field(title="주문자 ID")]
    status: Annotated[OrderStatus, Field(title="주문 상태")] = OrderStatus.PENDING
    total_price: Annotated[float, Field(ge=0, title="총 주문 금액")]
    items: Annotated[list[OrderItem], Field(title="주문 항목 목록")] = []
    created_at: Annotated[datetime, Field(title="생성 일시")] = Field(default_factory=datetime.now)
    updated_at: Annotated[datetime, Field(title="수정 일시")] = Field(default_factory=datetime.now)
