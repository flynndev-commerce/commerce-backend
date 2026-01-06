from collections.abc import Sequence

from app.application.dto.product_dto import ProductCreate, ProductRead, ProductUpdate
from app.core.exceptions import (
    ForbiddenException,
    ProductNotFoundException,
)
from app.domain.exceptions import InvalidDomainException
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

    async def update_product(self, seller_id: int, product_id: int, product_update: ProductUpdate) -> ProductRead:
        async with self.uow:
            product = await self.product_repository.get_by_id(product_id=product_id)
            if not product:
                raise ProductNotFoundException()

            if product.seller_id != seller_id:
                raise ForbiddenException(message="해당 상품에 대한 권한이 없습니다.")

            if product_update.name is not None:
                product.name = product_update.name

            if product_update.description is not None:
                product.description = product_update.description

            if product_update.price is not None:
                product.update_price(product_update.price)

            if product_update.stock is not None:
                # 재고 직접 수정 (단순 수정의 경우) -> 비즈니스적으로는 재고 추가/차감이 더 명확할 수 있으나
                # 여기서는 관리자/판매자가 수량을 조정하는 기능이므로 setter 역할
                if product_update.stock < 0:
                    raise InvalidDomainException("재고는 0보다 적을 수 없습니다.")  # 도메인 로직이 모델에 있으면 좋음
                product.stock = product_update.stock

            updated_product = await self.product_repository.update(product=product)
            return ProductRead.model_validate(updated_product)
