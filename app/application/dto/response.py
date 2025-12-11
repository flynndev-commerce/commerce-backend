from typing import Annotated

from pydantic import Field

from app.application.dto.base import CamelCaseBaseModel


class BaseResponse[T](CamelCaseBaseModel):
    code: Annotated[
        str,
        Field(title="응답 코드", description="API 처리 상태를 나타내는 코드"),
    ] = "OK"
    message: Annotated[
        str | None,
        Field(title="응답 메시지", description="API 처리 관련 메시지"),
    ] = None
    result: T
