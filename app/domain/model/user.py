from enum import StrEnum

import bcrypt
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.domain.model.seller import Seller


class UserRole(StrEnum):
    """사용자 역할"""

    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"


class User(BaseModel):
    """사용자 도메인 모델"""

    id: int | None = Field(default=None, title="고유 ID", description="사용자의 고유 식별자")
    email: EmailStr = Field(title="이메일", description="사용자 이메일 주소")
    full_name: str | None = Field(default=None, title="전체 이름", description="사용자의 전체 이름")
    hashed_password: str = Field(title="해시된 비밀번호", description="암호화된 사용자 비밀번호")
    is_active: bool = Field(default=True, title="활성 상태", description="사용자 계정의 활성화 여부")
    role: UserRole = Field(default=UserRole.BUYER, title="역할", description="사용자 역할 (구매자, 판매자, 관리자)")
    seller: Seller | None = Field(default=None, title="판매자 정보", description="사용자가 판매자인 경우 판매자 정보")

    model_config = ConfigDict(from_attributes=True)

    @property
    def is_seller(self) -> bool:
        """판매자 여부를 반환합니다."""
        return self.role == UserRole.SELLER

    @model_validator(mode="after")
    def set_role_if_seller_exists(self) -> "User":
        if self.seller is not None and self.role != UserRole.SELLER:
            self.role = UserRole.SELLER
        return self

    def update_info(self, full_name: str | None = None) -> None:
        """사용자 기본 정보를 수정합니다."""
        if full_name is not None:
            self.full_name = full_name

    def verify_password(self, password: str) -> bool:
        """비밀번호가 일치하는지 확인합니다."""
        return bcrypt.checkpw(password.encode("utf-8"), self.hashed_password.encode("utf-8"))

    def set_password(self, password: str) -> None:
        """비밀번호를 설정(해시화)합니다."""
        salt = bcrypt.gensalt()
        self.hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def promote_to_seller(self) -> None:
        """사용자를 판매자로 승격시킵니다."""
        if not self.is_seller:
            self.role = UserRole.SELLER
