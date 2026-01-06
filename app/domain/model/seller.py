from pydantic import BaseModel, ConfigDict, Field


class Seller(BaseModel):
    """판매자 도메인 모델"""

    id: int = Field(title="고유 ID", description="판매자의 고유 식별자")
    user_id: int = Field(title="사용자 ID", description="연결된 사용자의 ID")
    store_name: str = Field(title="상점명", description="판매자의 상점 이름")
    description: str | None = Field(default=None, title="상점 설명", description="상점에 대한 설명")

    model_config = ConfigDict(from_attributes=True)

    def update_info(self, store_name: str | None = None, description: str | None = None) -> None:
        """판매자 정보를 수정합니다."""
        if store_name is not None:
            self.store_name = store_name

        if description is not None:
            self.description = description
