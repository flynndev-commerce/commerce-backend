from datetime import datetime
from typing import Annotated, Any, ClassVar

from sqlalchemy import Column, Integer
from sqlmodel import Field, Relationship, SQLModel

from app.domain.model.order import OrderStatus

# Define explicit column for versioning to satisfy SQLAlchemy mapper args
version_col = Column("version", Integer, default=1, nullable=False)


class OrderEntity(SQLModel, table=True):
    __tablename__: ClassVar[str] = "order"
    __mapper_args__: ClassVar[dict[str, Any]] = {"version_id_col": version_col}

    id: Annotated[
        int | None,
        Field(default=None, primary_key=True, title="고유 ID"),
    ] = None
    user_id: Annotated[
        int,
        Field(foreign_key="user.id", index=True, title="주문자 ID"),
    ]
    status: Annotated[
        OrderStatus,
        Field(default=OrderStatus.PENDING, title="주문 상태"),
    ] = OrderStatus.PENDING
    total_price: Annotated[
        float,
        Field(ge=0, title="총 주문 금액"),
    ]
    created_at: Annotated[
        datetime,
        Field(default_factory=datetime.now, title="생성 일시"),
    ]
    updated_at: Annotated[
        datetime,
        Field(default_factory=datetime.now, title="수정 일시"),
    ]
    version: int | None = Field(default=1, sa_column=version_col)

    items: list["OrderItemEntity"] = Relationship(back_populates="order", sa_relationship_kwargs={"lazy": "selectin"})


class OrderItemEntity(SQLModel, table=True):
    __tablename__: ClassVar[str] = "order_item"

    id: Annotated[
        int | None,
        Field(default=None, primary_key=True, title="고유 ID"),
    ] = None
    order_id: Annotated[
        int | None,
        Field(foreign_key="order.id", index=True, title="주문 ID"),
    ] = None
    product_id: Annotated[
        int,
        Field(foreign_key="product.id", index=True, title="상품 ID"),
    ]
    price: Annotated[
        float,
        Field(gt=0, title="주문 당시 가격"),
    ]
    quantity: Annotated[
        int,
        Field(gt=0, title="주문 수량"),
    ]

    order: OrderEntity = Relationship(back_populates="items")
