from datetime import datetime
from typing import Annotated

from pydantic import Field

from app.application.dto.base import CamelCaseBaseModel
from app.domain.model.order import OrderStatus


class OrderItemCreate(CamelCaseBaseModel):
    """주문 항목 생성 DTO"""

    product_id: Annotated[int, Field(title="상품 ID")]
    quantity: Annotated[int, Field(gt=0, title="주문 수량")]


class OrderCreate(CamelCaseBaseModel):
    """주문 생성 DTO"""

    items: Annotated[list[OrderItemCreate], Field(min_length=1, title="주문 항목 목록")]


class OrderItemRead(CamelCaseBaseModel):
    """주문 항목 조회 DTO"""

    id: Annotated[int, Field(title="고유 ID")]
    product_id: Annotated[int, Field(title="상품 ID")]
    price: Annotated[float, Field(title="주문 당시 가격")]
    quantity: Annotated[int, Field(title="주문 수량")]


class OrderRead(CamelCaseBaseModel):
    """주문 조회 DTO"""

    id: Annotated[int, Field(title="고유 ID")]
    user_id: Annotated[int, Field(title="주문자 ID")]
    status: Annotated[OrderStatus, Field(title="주문 상태")]
    total_price: Annotated[float, Field(title="총 주문 금액")]
    items: Annotated[list[OrderItemRead], Field(title="주문 항목 목록")]
    created_at: Annotated[datetime, Field(title="생성 일시")]
    updated_at: Annotated[datetime, Field(title="수정 일시")]
