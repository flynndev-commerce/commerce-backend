from collections.abc import Sequence

from app.application.dto.product_dto import ProductCreate, ProductRead, ProductUpdate
from app.core.exceptions import ProductNotFoundException
from app.domain.model.product import Product
from app.domain.ports.product_repository import IProductRepository
from app.domain.ports.unit_of_work import IUnitOfWork


class ProductUseCase:
    def __init__(self, product_repository: IProductRepository, uow: IUnitOfWork):
        self.product_repository = product_repository
        self.uow = uow

    async def create_product(self, product_create: ProductCreate) -> ProductRead:
        async with self.uow:
            product_to_create = Product.model_validate(product_create)
            created_product = await self.product_repository.create(product=product_to_create)
            return ProductRead.model_validate(created_product)

    async def get_product_by_id(self, product_id: int) -> ProductRead:
        product = await self.product_repository.get_by_id(product_id=product_id)
        if not product:
            raise ProductNotFoundException()
        return ProductRead.model_validate(product)

    async def list_products(self, offset: int, limit: int) -> Sequence[ProductRead]:
        products = await self.product_repository.list(offset=offset, limit=limit)
        return [ProductRead.model_validate(p) for p in products]

    async def update_product(self, product_id: int, product_update: ProductUpdate) -> ProductRead:
        async with self.uow:
            product_to_update = await self.product_repository.get_by_id(product_id=product_id)
            if not product_to_update:
                raise ProductNotFoundException()

            update_data = product_update.model_dump(exclude_unset=True)
            updated_product_obj = product_to_update.model_copy(update=update_data)

            updated_product = await self.product_repository.update(product=updated_product_obj)
            return ProductRead.model_validate(updated_product)
