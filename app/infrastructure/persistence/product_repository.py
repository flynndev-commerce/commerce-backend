from collections.abc import Sequence

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.model.product import Product
from app.domain.ports.product_repository import IProductRepository
from app.infrastructure.persistence.models.product_entity import ProductEntity


class SQLProductRepository(IProductRepository):
    """SQL 데이터베이스에 대한 상품 리포지토리 구현체"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, product: Product) -> Product:
        db_product = ProductEntity.model_validate(product)
        self.session.add(db_product)
        await self.session.commit()
        await self.session.refresh(db_product)
        return Product.model_validate(db_product)

    async def get_by_id(self, product_id: int) -> Product | None:
        db_product = await self.session.get(ProductEntity, product_id)
        if db_product:
            return Product.model_validate(db_product)
        return None

    async def list(self, offset: int, limit: int) -> Sequence[Product]:
        statement = select(ProductEntity).offset(offset).limit(limit)
        result = await self.session.exec(statement)
        db_products = result.all()
        return [Product.model_validate(p) for p in db_products]

    async def update(self, product: Product) -> Product:
        if product.id is None:
            raise ValueError("업데이트를 위해서는 상품의 ID가 필요합니다.")

        db_product = await self.session.get(ProductEntity, product.id)
        if not db_product:
            raise ValueError("해당 ID의 상품을 찾을 수 없습니다.")

        product_data = product.model_dump(exclude_unset=True)
        for key, value in product_data.items():
            setattr(db_product, key, value)

        self.session.add(db_product)
        await self.session.commit()
        await self.session.refresh(db_product)
        return Product.model_validate(db_product)
