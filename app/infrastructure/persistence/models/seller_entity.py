from typing import TYPE_CHECKING, Annotated, ClassVar

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.user_entity import UserEntity


class SellerEntity(SQLModel, table=True):
    __tablename__: ClassVar[str] = "seller"

    id: Annotated[
        int | None,
        Field(
            default=None,
            primary_key=True,
            title="고유 ID",
            description="판매자의 고유 식별자",
        ),
    ]
    user_id: Annotated[
        int,
        Field(
            foreign_key="user.id",
            unique=True,
            index=True,
            title="사용자 ID",
            description="연결된 사용자의 ID",
        ),
    ]
    store_name: Annotated[
        str,
        Field(
            unique=True,
            index=True,
            title="상점명",
            description="판매자의 상점 이름",
        ),
    ]
    description: Annotated[
        str | None,
        Field(
            default=None,
            title="상점 설명",
            description="상점에 대한 설명",
        ),
    ]

    user: "UserEntity" = Relationship(back_populates="seller")
