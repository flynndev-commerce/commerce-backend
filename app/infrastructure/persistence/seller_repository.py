from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.model.seller import Seller
from app.domain.ports.seller_repository import ISellerRepository
from app.infrastructure.persistence.models.seller_entity import SellerEntity


class SQLSellerRepository(ISellerRepository):
    """SQLModel 기반 판매자 리포지토리 구현"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: int) -> Seller | None:
        statement = select(SellerEntity).where(SellerEntity.user_id == user_id)
        result = await self.session.exec(statement)
        entity = result.first()
        if entity:
            return Seller.model_validate(entity)
        return None

    async def save(self, seller: Seller) -> Seller:
        entity = SellerEntity(
            id=seller.id,
            user_id=seller.user_id,
            store_name=seller.store_name,
            description=seller.description,
        )

        if entity.id:
            entity = await self.session.merge(entity)
        else:
            self.session.add(entity)

        await self.session.flush()
        await self.session.refresh(entity)
        return Seller.model_validate(entity)
