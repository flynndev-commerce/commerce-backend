from typing import Annotated

from pydantic import Field

from app.application.dto.base import CamelCaseBaseModel


class CartItemCreate(CamelCaseBaseModel):
    """장바구니 항목 생성 DTO"""

    product_id: Annotated[int, Field(title="상품 ID")]
    quantity: Annotated[int, Field(gt=0, title="수량")]


class CartItemUpdate(CamelCaseBaseModel):
    """장바구니 항목 수정 DTO"""

    quantity: Annotated[int, Field(gt=0, title="수량")]


class CartItemRead(CamelCaseBaseModel):
    """장바구니 항목 조회 DTO"""

    id: Annotated[int, Field(title="장바구니 항목 ID")]
    product_id: Annotated[int, Field(title="상품 ID")]
    product_name: Annotated[str, Field(title="상품명")]
    price: Annotated[float, Field(title="단가")]
    quantity: Annotated[int, Field(title="수량")]
    total_price: Annotated[float, Field(title="총 금액")]


class CartRead(CamelCaseBaseModel):
    """장바구니 조회 DTO"""

    items: Annotated[list[CartItemRead], Field(title="장바구니 항목 목록")]
    total_price: Annotated[float, Field(title="총 주문 금액")]
