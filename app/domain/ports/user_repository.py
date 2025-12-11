from abc import ABC, abstractmethod

from app.domain.model.user import User


class IUserRepository(ABC):
    """사용자 리포지토리를 위한 포트(인터페이스)"""

    @abstractmethod
    async def create(self, user: User) -> User:
        """새로운 사용자를 생성합니다."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """이메일로 사용자를 조회합니다."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        """ID로 사용자를 조회합니다."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: User) -> User:
        """사용자 정보를 업데이트합니다."""
        raise NotImplementedError
