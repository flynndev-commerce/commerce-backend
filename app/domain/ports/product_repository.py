from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.domain.model.product import Product


class IProductRepository(ABC):
    """상품 리포지토리를 위한 포트(인터페이스)"""

    @abstractmethod
    async def create(self, product: Product) -> Product:
        """새로운 상품을 생성합니다."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, product_id: int) -> Product | None:
        """ID로 상품을 조회합니다."""
        raise NotImplementedError

    @abstractmethod
    async def list(self, offset: int, limit: int, seller_id: int | None = None) -> Sequence[Product]:
        """상품 목록을 조회합니다. seller_id가 제공되면 해당 판매자의 상품만 조회합니다."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, product: Product) -> Product:
        """상품 정보를 업데이트합니다."""
        raise NotImplementedError
