from collections.abc import Sequence
from typing import Any

from fastapi import HTTPException, status

from app.application.dto.order_dto import OrderCreate, OrderRead
from app.domain.model.order import Order, OrderItem, OrderStatus
from app.domain.ports.cart_repository import ICartRepository
from app.domain.ports.order_repository import IOrderRepository
from app.domain.ports.product_repository import IProductRepository
from app.domain.ports.unit_of_work import IUnitOfWork


class OrderUseCase:
    """주문 도메인 유즈케이스"""

    def __init__(
        self,
        order_repository: IOrderRepository,
        product_repository: IProductRepository,
        cart_repository: ICartRepository,
        uow: IUnitOfWork,
    ):
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.cart_repository = cart_repository
        self.uow = uow

    async def _create_order_core(self, user_id: int, items: Sequence[Any]) -> Order:
        """
        주문 생성 핵심 로직 (재고 확인, 차감, 주문 객체 생성 및 저장)
        items의 각 요소는 product_id와 quantity 속성을 가져야 합니다.
        """
        total_price = 0.0
        order_items = []

        for item in items:
            product = await self.product_repository.get_by_id(item.product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"상품을 찾을 수 없습니다. (ID: {item.product_id})",
                )

            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=(f"재고가 부족합니다. (상품: {product.name}, 재고: {product.stock}, 요청: {item.quantity})"),
                )

            # 가격 계산 및 아이템 생성
            item_price = product.price * item.quantity
            total_price += item_price

            order_items.append(
                OrderItem(
                    product_id=product.id,  # type: ignore
                    price=product.price,
                    quantity=item.quantity,
                )
            )

            # 재고 차감
            product.stock -= item.quantity
            await self.product_repository.update(product)

        # 주문 생성
        order = Order(
            user_id=user_id,
            total_price=total_price,
            items=order_items,
        )

        return await self.order_repository.save(order)

    async def create_order(self, user_id: int, order_create: OrderCreate) -> OrderRead:
        """
        주문을 생성합니다.
        1. 상품 존재 여부 및 재고 확인
        2. 총 주문 금액 계산
        3. 재고 차감 (트랜잭션 처리)
        4. 주문 저장
        """
        async with self.uow:
            saved_order = await self._create_order_core(user_id, order_create.items)

            # 주문한 상품이 장바구니에 있다면 제거
            product_ids = [item.product_id for item in order_create.items]
            await self.cart_repository.delete_items_by_user_id(user_id, product_ids)

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

    async def cancel_order(self, user_id: int, order_id: int) -> OrderRead:
        """
        주문을 취소합니다.
        1. 주문 조회 및 권한 확인
        2. 주문 상태 확인 (PENDING, PAID만 취소 가능)
        3. 재고 복구
        4. 주문 상태 변경 및 저장
        """
        async with self.uow:
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

            if order.status not in [OrderStatus.PENDING, OrderStatus.PAID]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 배송이 시작되었거나 취소된 주문은 취소할 수 없습니다.",
                )

            # 재고 복구
            for item in order.items:
                product = await self.product_repository.get_by_id(item.product_id)
                if product:
                    product.stock += item.quantity
                    await self.product_repository.update(product)

            # 상태 변경
            order.status = OrderStatus.CANCELLED
            updated_order = await self.order_repository.save(order)

            return OrderRead.model_validate(updated_order)

    async def create_order_from_cart(self, user_id: int) -> OrderRead:
        """
        장바구니에 있는 모든 상품을 주문합니다.
        1. 장바구니 조회
        2. 재고 확인 및 차감
        3. 주문 생성
        4. 장바구니 비우기
        """
        async with self.uow:
            cart_items = await self.cart_repository.get_all_by_user_id(user_id)
            if not cart_items:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="장바구니가 비어있습니다.",
                )

            saved_order = await self._create_order_core(user_id, cart_items)

            # 장바구니 비우기
            await self.cart_repository.delete_all_by_user_id(user_id)

            return OrderRead.model_validate(saved_order)
