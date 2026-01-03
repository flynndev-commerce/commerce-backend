from typing import Annotated

from pydantic import Field

from app.application.dto.base import CamelCaseBaseModel


class SellerCreate(CamelCaseBaseModel):
    store_name: Annotated[str, Field(title="상점명", description="판매자의 상점 이름")]
    description: Annotated[str | None, Field(default=None, title="상점 설명", description="상점에 대한 설명")]


class SellerRead(CamelCaseBaseModel):
    id: Annotated[int, Field(title="고유 ID", description="판매자의 고유 식별자")]
    user_id: Annotated[int, Field(title="사용자 ID", description="연결된 사용자의 ID")]
    store_name: Annotated[str, Field(title="상점명", description="판매자의 상점 이름")]
    description: Annotated[str | None, Field(default=None, title="상점 설명", description="상점에 대한 설명")]
