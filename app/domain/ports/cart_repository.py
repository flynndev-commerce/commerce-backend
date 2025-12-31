from abc import ABC, abstractmethod

from app.domain.model.cart import CartItem


class ICartRepository(ABC):
    """장바구니 리포지토리 인터페이스"""

    @abstractmethod
    async def get_by_user_and_product(self, user_id: int, product_id: int) -> CartItem | None:
        """사용자 ID와 상품 ID로 장바구니 항목을 조회합니다."""
        pass

    @abstractmethod
    async def get_all_by_user_id(self, user_id: int) -> list[CartItem]:
        """사용자의 모든 장바구니 항목을 조회합니다."""
        pass

    @abstractmethod
    async def save(self, cart_item: CartItem) -> CartItem:
        """장바구니 항목을 저장하거나 업데이트합니다."""
        pass

    @abstractmethod
    async def delete(self, cart_item: CartItem) -> None:
        """장바구니 항목을 삭제합니다."""
        pass
