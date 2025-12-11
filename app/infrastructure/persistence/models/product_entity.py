from typing import Annotated, ClassVar

from sqlmodel import Field, SQLModel


class ProductEntity(SQLModel, table=True):
    __tablename__: ClassVar[str] = "product"

    id: Annotated[
        int | None,
        Field(
            default=None,
            primary_key=True,
            title="고유 ID",
            description="상품의 고유 식별자",
        ),
    ]
    name: Annotated[
        str,
        Field(index=True, title="상품명", description="상품의 이름"),
    ]
    description: Annotated[
        str | None,
        Field(default=None, title="상품 설명", description="상품에 대한 상세 설명"),
    ]
    price: Annotated[
        float,
        Field(title="가격", description="상품의 가격"),
    ]
    stock: Annotated[
        int,
        Field(title="재고 수량", description="남아있는 상품의 수량"),
    ]
