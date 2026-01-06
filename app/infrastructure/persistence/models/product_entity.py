from typing import TYPE_CHECKING, Annotated, ClassVar

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.seller_entity import SellerEntity


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
    ] = None
    name: Annotated[
        str,
        Field(index=True, title="상품명", description="상품의 이름"),
    ]
    description: Annotated[
        str | None,
        Field(default=None, title="상품 설명", description="상품에 대한 상세 설명"),
    ] = None
    price: Annotated[
        float,
        Field(title="가격", description="상품의 가격"),
    ]
    stock: Annotated[
        int,
        Field(title="재고 수량", description="남아있는 상품의 수량"),
    ]
    seller_id: Annotated[
        int,
        Field(foreign_key="seller.id", title="판매자 ID", description="상품을 등록한 판매자의 ID"),
    ]

    seller: "SellerEntity" = Relationship(back_populates="products")
