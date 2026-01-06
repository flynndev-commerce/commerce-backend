from app.domain.model.cart import CartItem
from app.domain.ports.cart_repository import ICartRepository


class FakeCartRepository(ICartRepository):
    def __init__(self) -> None:
        self._data: dict[int, CartItem] = {}
        self._next_id = 1

    async def get_by_user_and_product(self, user_id: int, product_id: int) -> CartItem | None:
        for item in self._data.values():
            if item.user_id == user_id and item.product_id == product_id:
                return item
        return None

    async def get_all_by_user_id(self, user_id: int) -> list[CartItem]:
        return [item for item in self._data.values() if item.user_id == user_id]

    async def save(self, cart_item: CartItem) -> CartItem:
        if cart_item.id is None:
            cart_item.id = self._next_id
            self._next_id += 1

        if cart_item.id is not None:
            self._data[cart_item.id] = cart_item
        return cart_item

    async def delete(self, cart_item: CartItem) -> None:
        if cart_item.id is not None and cart_item.id in self._data:
            del self._data[cart_item.id]

    async def delete_by_user_and_product(self, user_id: int, product_id: int) -> None:
        item = await self.get_by_user_and_product(user_id, product_id)
        if item and item.id is not None:
            if item.id in self._data:
                del self._data[item.id]

    async def delete_items_by_user_id(self, user_id: int, product_ids: list[int]) -> None:
        items_to_delete = []
        for item in self._data.values():
            if item.user_id == user_id and item.product_id in product_ids:
                items_to_delete.append(item.id)

        for item_id in items_to_delete:
            if item_id is not None and item_id in self._data:
                del self._data[item_id]

    async def delete_all_by_user_id(self, user_id: int) -> None:
        items_to_delete = [item.id for item in self._data.values() if item.user_id == user_id]
        for item_id in items_to_delete:
            if item_id is not None and item_id in self._data:
                del self._data[item_id]
