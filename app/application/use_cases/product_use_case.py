from collections.abc import Sequence

from app.application.dto.product_dto import ProductCreate, ProductRead, ProductUpdate
from app.core.decorators import retry_on_conflict
from app.core.exceptions import (
    ProductNotFoundException,
)
from app.domain.model.product import Product
from app.domain.ports.product_repository import IProductRepository
from app.domain.ports.unit_of_work import IUnitOfWork


class ProductUseCase:
    def __init__(self, product_repository: IProductRepository, uow: IUnitOfWork):
        self.product_repository = product_repository
        self.uow = uow

    async def create_product(self, seller_id: int, product_create: ProductCreate) -> ProductRead:
        async with self.uow:
            product_data = product_create.model_dump()
            product_to_create = Product(**product_data, seller_id=seller_id)
            created_product = await self.product_repository.create(product=product_to_create)
            return ProductRead.model_validate(created_product)

    async def get_product_by_id(self, product_id: int) -> ProductRead:
        product = await self.product_repository.get_by_id(product_id=product_id)
        if not product:
            raise ProductNotFoundException()
        return ProductRead.model_validate(product)

    async def list_products(self, offset: int, limit: int, seller_id: int | None = None) -> Sequence[ProductRead]:
        products = await self.product_repository.list(offset=offset, limit=limit, seller_id=seller_id)
        return [ProductRead.model_validate(p) for p in products]

    @retry_on_conflict()
    async def update_product(self, seller_id: int, product_id: int, product_update: ProductUpdate) -> ProductRead:
        async with self.uow:
            product = await self.product_repository.get_by_id(product_id=product_id)
            if not product:
                raise ProductNotFoundException()

            product.verify_owner(seller_id)

            product.update_details(
                name=product_update.name,
                description=product_update.description,
                price=product_update.price,
                stock=product_update.stock,
            )

            updated_product = await self.product_repository.update(product=product)
            return ProductRead.model_validate(updated_product)
