from typing import Annotated

from pydantic import BaseModel, Field


class BaseResponse[T](BaseModel):
    code: Annotated[
        str,
        Field(title="응답 코드", description="API 처리 상태를 나타내는 코드"),
    ] = "OK"
    message: Annotated[
        str | None,
        Field(title="응답 메시지", description="API 처리 관련 메시지"),
    ] = None
    result: T


class Token(BaseModel):
    access_token: Annotated[str, Field(title="액세스 토큰", description="인증에 사용되는 JWT 토큰")]
    token_type: Annotated[str, Field(title="토큰 타입", description="토큰의 타입 (예: Bearer)")] = "bearer"
