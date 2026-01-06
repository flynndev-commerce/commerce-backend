from typing import Annotated, ClassVar

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from app.infrastructure.persistence.models.product_entity import ProductEntity
from app.infrastructure.persistence.models.user_entity import UserEntity


class CartItemEntity(SQLModel, table=True):
    __tablename__: ClassVar[str] = "cart_item"
    __table_args__ = (UniqueConstraint("user_id", "product_id"),)

    id: Annotated[
        int | None,
        Field(default=None, primary_key=True, title="고유 ID"),
    ] = None
    user_id: Annotated[
        int,
        Field(foreign_key="user.id", index=True, title="사용자 ID"),
    ]
    product_id: Annotated[
        int,
        Field(foreign_key="product.id", index=True, title="상품 ID"),
    ]
    quantity: Annotated[
        int,
        Field(gt=0, title="수량"),
    ]

    # Relationships
    # Note: We are not defining back_populates on UserEntity/ProductEntity to avoid modifying them for now.
    # This allows us to eager load product details when querying cart items.
    product: ProductEntity = Relationship()
    user: UserEntity = Relationship()
