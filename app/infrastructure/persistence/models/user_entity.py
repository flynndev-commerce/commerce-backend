from typing import TYPE_CHECKING, Annotated, ClassVar

from sqlmodel import Field, Relationship, SQLModel

from app.domain.model.user import UserRole

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.seller_entity import SellerEntity


class UserEntity(SQLModel, table=True):
    __tablename__: ClassVar[str] = "user"

    id: Annotated[
        int | None,
        Field(
            default=None,
            primary_key=True,
            title="고유 ID",
            description="사용자의 고유 식별자",
        ),
    ] = None
    email: Annotated[
        str,
        Field(
            unique=True,
            index=True,
            title="이메일",
            description="사용자 이메일 주소, 로그인 시 사용",
        ),
    ]
    full_name: Annotated[
        str | None,
        Field(default=None, title="전체 이름", description="사용자의 전체 이름"),
    ] = None
    hashed_password: Annotated[
        str,
        Field(title="해시된 비밀번호", description="암호화되어 저장되는 사용자 비밀번호"),
    ]
    is_active: Annotated[
        bool,
        Field(default=True, title="활성 상태", description="사용자 계정의 활성화 여부"),
    ] = True
    role: Annotated[
        UserRole,
        Field(
            default=UserRole.BUYER,
            title="역할",
            description="사용자 역할 (구매자, 판매자, 관리자)",
        ),
    ] = UserRole.BUYER

    seller: "SellerEntity" = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
