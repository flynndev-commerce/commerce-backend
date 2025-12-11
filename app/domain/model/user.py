import bcrypt
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """사용자 도메인 모델"""

    id: int | None = Field(default=None, title="고유 ID", description="사용자의 고유 식별자")
    email: EmailStr = Field(title="이메일", description="사용자 이메일 주소")
    full_name: str | None = Field(default=None, title="전체 이름", description="사용자의 전체 이름")
    hashed_password: str = Field(title="해시된 비밀번호", description="암호화된 사용자 비밀번호")
    is_active: bool = Field(default=True, title="활성 상태", description="사용자 계정의 활성화 여부")

    class Config:
        from_attributes = True

    def check_password(self, password: str) -> bool:
        """제공된 비밀번호가 해시된 비밀번호와 일치하는지 확인합니다."""
        return bcrypt.checkpw(password.encode("utf-8"), self.hashed_password.encode("utf-8"))
