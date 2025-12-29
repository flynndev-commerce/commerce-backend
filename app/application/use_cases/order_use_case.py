from fastapi import HTTPException, status

from app.application.dto.order_dto import OrderCreate, OrderRead
from app.domain.model.order import Order, OrderItem
from app.domain.ports.order_repository import IOrderRepository
from app.domain.ports.product_repository import IProductRepository


class OrderUseCase:
    """주문 도메인 유즈케이스"""

    def __init__(
        self,
        order_repository: IOrderRepository,
        product_repository: IProductRepository,
    ):
        self.order_repository = order_repository
        self.product_repository = product_repository

    async def create_order(self, user_id: int, order_create: OrderCreate) -> OrderRead:
        """
        주문을 생성합니다.
        1. 상품 존재 여부 및 재고 확인
        2. 총 주문 금액 계산
        3. 재고 차감 (TODO: 트랜잭션 처리 필요)
        4. 주문 저장
        """
        total_price = 0.0
        order_items = []

        for item_create in order_create.items:
            product = await self.product_repository.get_by_id(item_create.product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"상품을 찾을 수 없습니다. (ID: {item_create.product_id})",
                )

            if product.stock < item_create.quantity:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=(
                        f"재고가 부족합니다. (상품: {product.name}, "
                        f"재고: {product.stock}, 요청: {item_create.quantity})"
                    ),
                )

            # 가격 계산 및 아이템 생성
            item_price = product.price * item_create.quantity
            total_price += item_price

            order_items.append(
                OrderItem(
                    product_id=product.id,  # type: ignore
                    price=product.price,
                    quantity=item_create.quantity,
                )
            )

            # 재고 차감
            product.stock -= item_create.quantity
            await self.product_repository.update(product)

        # 주문 생성
        order = Order(
            user_id=user_id,
            total_price=total_price,
            items=order_items,
        )

        saved_order = await self.order_repository.save(order)
        return OrderRead.model_validate(saved_order)

    async def list_orders(self, user_id: int, offset: int, limit: int) -> list[OrderRead]:
        """사용자의 주문 목록을 조회합니다."""
        orders = await self.order_repository.find_by_user_id(user_id, offset, limit)
        return [OrderRead.model_validate(order) for order in orders]

    async def get_order(self, user_id: int, order_id: int) -> OrderRead:
        """주문 상세 정보를 조회합니다."""
        order = await self.order_repository.find_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="주문을 찾을 수 없습니다.",
            )

        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="해당 주문에 대한 권한이 없습니다.",
            )

        return OrderRead.model_validate(order)
