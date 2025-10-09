from typing import Annotated

from pydantic import BaseModel, Field


class TokenPayload(BaseModel):
    sub: Annotated[str, Field(title="주제", description="토큰의 주체 (예: 사용자 이메일)")]
