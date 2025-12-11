from typing import Annotated

from pydantic import Field

from app.application.dto.base import CamelCaseBaseModel


class ProductBase(CamelCaseBaseModel):
    name: Annotated[str, Field(title="상품명")]
    description: Annotated[str | None, Field(title="상품 설명")] = None
    price: Annotated[float, Field(title="가격", gt=0)]
    stock: Annotated[int, Field(title="재고 수량", ge=0)]


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: Annotated[int, Field(title="고유 ID")]


class ProductUpdate(CamelCaseBaseModel):
    name: Annotated[str | None, Field(title="상품명")] = None
    description: Annotated[str | None, Field(title="상품 설명")] = None
    price: Annotated[float | None, Field(title="가격", gt=0)] = None
    stock: Annotated[int | None, Field(title="재고 수량", ge=0)] = None
