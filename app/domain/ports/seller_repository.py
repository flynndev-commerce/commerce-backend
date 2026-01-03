from abc import ABC, abstractmethod

from app.domain.model.seller import Seller


class ISellerRepository(ABC):
    """판매자 리포지토리 인터페이스"""

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> Seller | None:
        """사용자 ID로 판매자 정보를 조회합니다."""
        pass

    @abstractmethod
    async def save(self, seller: Seller) -> Seller:
        """판매자 정보를 저장하거나 업데이트합니다."""
        pass
