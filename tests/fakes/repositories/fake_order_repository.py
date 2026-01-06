from app.domain.model.order import Order
from app.domain.ports.order_repository import IOrderRepository


class FakeOrderRepository(IOrderRepository):
    def __init__(self) -> None:
        self._data: dict[int, Order] = {}
        self._next_id = 1

    async def save(self, order: Order) -> Order:
        if order.id is None:
            order.id = self._next_id
            self._next_id += 1

        if order.id is not None:
            self._data[order.id] = order
        return order

    async def find_by_id(self, order_id: int) -> Order | None:
        return self._data.get(order_id)

    async def find_all(self, skip: int, limit: int) -> list[Order]:
        orders = list(self._data.values())
        return orders[skip : skip + limit]

    async def find_by_user_id(self, user_id: int, skip: int, limit: int) -> list[Order]:
        orders = [o for o in self._data.values() if o.user_id == user_id]
        return orders[skip : skip + limit]
