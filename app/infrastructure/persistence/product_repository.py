from collections.abc import Sequence

from sqlalchemy.orm.exc import StaleDataError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.exceptions import ConcurrentModificationException
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
        await self.session.flush()
        await self.session.refresh(db_product)
        return Product.model_validate(db_product)

    async def get_by_id(self, product_id: int) -> Product | None:
        db_product = await self.session.get(ProductEntity, product_id)
        if db_product:
            return Product.model_validate(db_product)
        return None

    async def list(self, offset: int, limit: int, seller_id: int | None = None) -> Sequence[Product]:
        statement = select(ProductEntity)
        if seller_id is not None:
            statement = statement.where(ProductEntity.seller_id == seller_id)

        statement = statement.offset(offset).limit(limit)
        result = await self.session.exec(statement)
        db_products = result.all()
        return [Product.model_validate(p) for p in db_products]

    async def update(self, product: Product) -> Product:
        if product.id is None:
            raise ValueError("업데이트를 위해서는 상품의 ID가 필요합니다.")

        # 낙관적 락(Optimistic Lock): SQLAlchemy version_id_col 사용
        # 1. DB에서 엔티티 로드
        db_product = await self.session.get(ProductEntity, product.id)
        if not db_product:
            raise ValueError("해당 ID의 상품을 찾을 수 없습니다.")

        # 2. 클라이언트 요청 버전 할당 (중요)
        # SQLAlchemy가 UPDATE 시 WHERE id=? AND version=? 쿼리를 생성하기 위해
        # 현재 메모리 상의 객체 버전을 클라이언트가 보낸 버전으로 맞춰야 합니다.
        # 만약 db_product.version(DB최신) != product.version(요청) 이라면
        # 아래 flush 시점에 StaleDataError가 발생합니다.
        # (단, session.get으로 가져온 시점에 이미 DB 버전이 높다면 로직에 따라 다름)

        # 더 확실한 방법:
        # 사용자가 보낸 version을 '믿고' 업데이트를 시도합니다.
        # db_product는 현재 세션에 attach된 상태입니다.
        if product.version != db_product.version:
            # 이미 DB가 앞서 나간 경우 (Fast Fail)
            raise ConcurrentModificationException(
                f"상품 정보가 변경되었습니다. 최신 정보를 다시 확인해주세요. (ID: {product.id})"
            )

        # 3. 필드 업데이트
        product_data = product.model_dump(exclude_unset=True)
        for key, value in product_data.items():
            if key not in ["id", "version"]:
                setattr(db_product, key, value)

        try:
            self.session.add(db_product)
            await self.session.flush()
            await self.session.refresh(db_product)
            return Product.model_validate(db_product)
        except StaleDataError as e:
            await self.session.rollback()
            raise ConcurrentModificationException(
                f"상품 정보가 변경되었습니다. 최신 정보를 다시 확인해주세요. (ID: {product.id})"
            ) from e
