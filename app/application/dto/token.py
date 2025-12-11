from typing import Annotated

from pydantic import Field

from app.application.dto.base import CamelCaseBaseModel


class Token(CamelCaseBaseModel):
    access_token: Annotated[str, Field(title="액세스 토큰", description="인증에 사용되는 JWT 토큰")]
    token_type: Annotated[str, Field(title="토큰 타입", description="토큰의 타입 (예: Bearer)")] = "bearer"


class TokenPayload(CamelCaseBaseModel):
    sub: Annotated[str, Field(title="주제", description="토큰의 주체 (예: 사용자 이메일)")]
