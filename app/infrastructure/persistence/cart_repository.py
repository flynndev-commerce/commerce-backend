from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.model.cart import CartItem
from app.domain.ports.cart_repository import ICartRepository
from app.infrastructure.persistence.models.cart_entity import CartItemEntity


class SQLCartRepository(ICartRepository):
    """SQLModel 기반 장바구니 리포지토리 구현"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_and_product(self, user_id: int, product_id: int) -> CartItem | None:
        statement = select(CartItemEntity).where(
            CartItemEntity.user_id == user_id,
            CartItemEntity.product_id == product_id,
        )
        result = await self.session.exec(statement)
        entity = result.first()
        if entity:
            return CartItem.model_validate(entity)
        return None

    async def get_all_by_user_id(self, user_id: int) -> list[CartItem]:
        statement = select(CartItemEntity).where(CartItemEntity.user_id == user_id)
        result = await self.session.exec(statement)
        entities = result.all()
        return [CartItem.model_validate(entity) for entity in entities]

    async def save(self, cart_item: CartItem) -> CartItem:
        entity = CartItemEntity(
            id=cart_item.id,
            user_id=cart_item.user_id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
        )

        if entity.id:
            entity = await self.session.merge(entity)
        else:
            self.session.add(entity)

        await self.session.flush()
        await self.session.refresh(entity)
        return CartItem.model_validate(entity)

    async def delete(self, cart_item: CartItem) -> None:
        if cart_item.id:
            entity = await self.session.get(CartItemEntity, cart_item.id)
            if entity:
                await self.session.delete(entity)

    async def delete_by_user_and_product(self, user_id: int, product_id: int) -> None:
        statement = select(CartItemEntity).where(
            CartItemEntity.user_id == user_id,
            CartItemEntity.product_id == product_id,
        )
        result = await self.session.exec(statement)
        entity = result.first()
        if entity:
            await self.session.delete(entity)

    async def delete_items_by_user_id(self, user_id: int, product_ids: list[int]) -> None:
        if not product_ids:
            return
        statement = select(CartItemEntity).where(
            CartItemEntity.user_id == user_id,
            CartItemEntity.product_id.in_(product_ids),  # type: ignore
        )
        result = await self.session.exec(statement)
        entities = result.all()
        for entity in entities:
            await self.session.delete(entity)

    async def delete_all_by_user_id(self, user_id: int) -> None:
        statement = select(CartItemEntity).where(CartItemEntity.user_id == user_id)
        result = await self.session.exec(statement)
        entities = result.all()
        for entity in entities:
            await self.session.delete(entity)
