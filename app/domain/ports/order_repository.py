from abc import ABC, abstractmethod

from app.domain.model.order import Order


class IOrderRepository(ABC):
    """주문 리포지토리 인터페이스"""

    @abstractmethod
    async def save(self, order: Order) -> Order:
        """주문을 저장하거나 업데이트합니다."""
        pass

    @abstractmethod
    async def find_by_id(self, order_id: int) -> Order | None:
        """ID로 주문을 조회합니다."""
        pass

    @abstractmethod
    async def find_all(self, skip: int, limit: int) -> list[Order]:
        """모든 주문 목록을 조회합니다."""
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: int, skip: int, limit: int) -> list[Order]:
        """사용자 ID로 주문 목록을 조회합니다."""
        pass
