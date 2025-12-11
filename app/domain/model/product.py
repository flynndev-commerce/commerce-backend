from pydantic import BaseModel, Field


class Product(BaseModel):
    """상품 도메인 모델"""

    id: int | None = Field(default=None, title="고유 ID", description="상품의 고유 식별자")
    name: str = Field(title="상품명", description="상품의 이름")
    description: str | None = Field(default=None, title="상품 설명", description="상품에 대한 상세 설명")
    price: float = Field(gt=0, title="가격", description="상품의 가격. 0보다 커야 합니다.")
    stock: int = Field(ge=0, title="재고 수량", description="남아있는 상품의 수량. 0 이상이어야 합니다.")

    class Config:
        from_attributes = True
