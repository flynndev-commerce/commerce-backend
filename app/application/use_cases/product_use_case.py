from collections.abc import Sequence

from fastapi import HTTPException, status

from app.application.dto.product_dto import ProductCreate, ProductRead, ProductUpdate
from app.domain.model.product import Product
from app.domain.ports.product_repository import IProductRepository


class ProductUseCase:
    def __init__(self, product_repository: IProductRepository):
        self.product_repository = product_repository

    async def create_product(self, product_create: ProductCreate) -> ProductRead:
        product_to_create = Product.model_validate(product_create)
        created_product = await self.product_repository.create(product=product_to_create)
        return ProductRead.model_validate(created_product)

    async def get_product_by_id(self, product_id: int) -> ProductRead:
        product = await self.product_repository.get_by_id(product_id=product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="상품을 찾을 수 없습니다.",
            )
        return ProductRead.model_validate(product)

    async def list_products(self, offset: int, limit: int) -> Sequence[ProductRead]:
        products = await self.product_repository.list(offset=offset, limit=limit)
        return [ProductRead.model_validate(p) for p in products]

    async def update_product(self, product_id: int, product_update: ProductUpdate) -> ProductRead:
        product_to_update = await self.product_repository.get_by_id(product_id=product_id)
        if not product_to_update:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="상품을 찾을 수 없습니다.",
            )

        update_data = product_update.model_dump(exclude_unset=True)
        updated_product_obj = product_to_update.model_copy(update=update_data)

        updated_product = await self.product_repository.update(product=updated_product_obj)
        return ProductRead.model_validate(updated_product)
