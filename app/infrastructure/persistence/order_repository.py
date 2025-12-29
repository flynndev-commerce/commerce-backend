from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.model.order import Order, OrderItem
from app.domain.ports.order_repository import IOrderRepository
from app.infrastructure.persistence.models.order_entity import OrderEntity, OrderItemEntity


class SQLOrderRepository(IOrderRepository):
    """SQLModel 기반 주문 리포지토리 구현"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, order: Order) -> Order:
        # Order 도메인 모델 -> OrderEntity 변환
        order_entity = OrderEntity(
            id=order.id,
            user_id=order.user_id,
            status=order.status,
            total_price=order.total_price,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )

        # OrderItem 도메인 모델 -> OrderItemEntity 변환
        order_item_entities = [
            OrderItemEntity(
                id=item.id,
                product_id=item.product_id,
                price=item.price,
                quantity=item.quantity,
            )
            for item in order.items
        ]
        order_entity.items = order_item_entities

        if order.id:
            order_entity = await self.session.merge(order_entity)
        else:
            self.session.add(order_entity)

        await self.session.commit()
        await self.session.refresh(order_entity)

        return self._to_domain(order_entity)

    async def find_by_id(self, order_id: int) -> Order | None:
        statement = select(OrderEntity).where(OrderEntity.id == order_id).options(selectinload(OrderEntity.items))  # type: ignore
        result = await self.session.exec(statement)
        order_entity = result.first()

        if not order_entity:
            return None

        return self._to_domain(order_entity)

    async def find_all(self, skip: int, limit: int) -> list[Order]:
        statement = select(OrderEntity).offset(skip).limit(limit).options(selectinload(OrderEntity.items))  # type: ignore
        result = await self.session.exec(statement)
        order_entities = result.all()

        return [self._to_domain(entity) for entity in order_entities]

    async def find_by_user_id(self, user_id: int, skip: int, limit: int) -> list[Order]:
        statement = (
            select(OrderEntity)
            .where(OrderEntity.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .options(selectinload(OrderEntity.items))  # type: ignore
        )
        result = await self.session.exec(statement)
        order_entities = result.all()

        return [self._to_domain(entity) for entity in order_entities]

    def _to_domain(self, entity: OrderEntity) -> Order:
        """OrderEntity를 Order 도메인 모델로 변환"""
        items = [
            OrderItem(
                id=item.id,
                product_id=item.product_id,
                price=item.price,
                quantity=item.quantity,
            )
            for item in entity.items
        ]

        return Order(
            id=entity.id,
            user_id=entity.user_id,
            status=entity.status,
            total_price=entity.total_price,
            items=items,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
