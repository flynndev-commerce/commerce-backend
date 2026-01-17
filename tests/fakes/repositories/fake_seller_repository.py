from app.domain.model.seller import Seller
from app.domain.ports.seller_repository import ISellerRepository


class FakeSellerRepository(ISellerRepository):
    def __init__(self) -> None:
        self._data: dict[int, Seller] = {}
        self._next_id = 1

    async def get_by_user_id(self, user_id: int) -> Seller | None:
        for seller in self._data.values():
            if seller.user_id == user_id:
                return seller
        return None

    async def create(self, user_id: int, store_name: str, description: str | None = None) -> Seller:
        seller = Seller(
            id=self._next_id,
            user_id=user_id,
            store_name=store_name,
            description=description,
        )
        self._data[self._next_id] = seller
        self._next_id += 1
        return seller

    async def update(self, seller: Seller) -> Seller:
        if seller.id in self._data:
            self._data[seller.id] = seller
        return seller
