from collections.abc import Sequence

from app.domain.model.product import Product
from app.domain.ports.product_repository import IProductRepository


class FakeProductRepository(IProductRepository):
    def __init__(self) -> None:
        self._data: dict[int, Product] = {}
        self._next_id = 1

    async def create(self, product: Product) -> Product:
        if product.id is None:
            product.id = self._next_id
            self._next_id += 1

        if product.id is not None:
            self._data[product.id] = product
        return product

    async def get_by_id(self, product_id: int) -> Product | None:
        return self._data.get(product_id)

    async def list(self, offset: int, limit: int, seller_id: int | None = None) -> Sequence[Product]:
        products = list(self._data.values())
        if seller_id is not None:
            products = [p for p in products if p.seller_id == seller_id]

        return products[offset : offset + limit]

    async def update(self, product: Product) -> Product:
        if product.id is not None and product.id in self._data:
            self._data[product.id] = product
        return product
