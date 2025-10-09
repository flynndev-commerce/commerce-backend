from typing import Annotated

from pydantic import Field

from app.schemas.base import CamelCaseBaseModel


class TokenPayload(CamelCaseBaseModel):
    sub: Annotated[str, Field(title="주제", description="토큰의 주체 (예: 사용자 이메일)")]
