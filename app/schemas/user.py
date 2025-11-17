from typing import Annotated

from pydantic import EmailStr, Field

from app.schemas.base import CamelCaseBaseModel


# 사용자 스키마의 공통 기본 속성
class UserBase(CamelCaseBaseModel):
    email: Annotated[EmailStr, Field(title="이메일", description="사용자 이메일 주소")]
    full_name: Annotated[
        str | None,
        Field(default=None, title="전체 이름", description="사용자의 전체 이름"),
    ]


# 사용자 생성을 위한 스키마
class UserCreate(UserBase):
    password: Annotated[
        str,
        Field(min_length=8, title="비밀번호", description="사용자 비밀번호 (8자 이상)"),
    ]


# 사용자 정보 조회를 위한 스키마 (API 응답용)
class UserRead(UserBase):
    id: Annotated[int, Field(title="고유 ID", description="사용자의 고유 식별자")]
    is_active: Annotated[bool, Field(title="활성 상태", description="사용자 계정의 활성화 여부")]


# 사용자 로그인을 위한 스키마
class UserLogin(CamelCaseBaseModel):
    email: Annotated[EmailStr, Field(title="이메일", description="사용자 이메일 주소")]
    password: Annotated[str, Field(title="비밀번호", description="사용자 비밀번호")]


# 사용자 정보 수정을 위한 스키마
class UserUpdate(CamelCaseBaseModel):
    full_name: Annotated[
        str | None,
        Field(default=None, title="전체 이름", description="사용자의 전체 이름"),
    ]
    password: Annotated[
        str | None,
        Field(default=None, min_length=8, title="비밀번호", description="새로운 비밀번호 (8자 이상)"),
    ]
