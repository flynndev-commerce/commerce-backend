from typing import Annotated, ClassVar

from sqlmodel import Field, SQLModel


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
    ]
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
    ]
    hashed_password: Annotated[
        str,
        Field(title="해시된 비밀번호", description="암호화되어 저장되는 사용자 비밀번호"),
    ]
    is_active: Annotated[
        bool,
        Field(default=True, title="활성 상태", description="사용자 계정의 활성화 여부"),
    ]
