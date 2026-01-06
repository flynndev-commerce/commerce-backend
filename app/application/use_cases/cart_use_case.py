from app.application.dto.cart_dto import (
    CartItemCreate,
    CartItemRead,
    CartItemUpdate,
    CartRead,
)
from app.core.exceptions import (
    CartItemNotFoundException,
    InsufficientStockException,
    ProductNotFoundException,
)
from app.domain.exceptions import InvalidDomainException
from app.domain.model.cart import CartItem
from app.domain.ports.cart_repository import ICartRepository
from app.domain.ports.product_repository import IProductRepository
from app.domain.ports.unit_of_work import IUnitOfWork


class CartUseCase:
    """장바구니 도메인 유즈케이스"""

    def __init__(
        self,
        cart_repository: ICartRepository,
        product_repository: IProductRepository,
        uow: IUnitOfWork,
    ):
        self.cart_repository = cart_repository
        self.product_repository = product_repository
        self.uow = uow

    async def get_cart(self, user_id: int) -> CartRead:
        """사용자의 장바구니를 조회합니다."""
        cart_items = await self.cart_repository.get_all_by_user_id(user_id)

        items_read = []
        for item in cart_items:
            product = await self.product_repository.get_by_id(item.product_id)
            if not product:
                # 상품이 삭제된 경우 장바구니에서도 제거하거나 무시
                continue

            items_read.append(
                CartItemRead(
                    id=item.id,  # type: ignore
                    product_id=item.product_id,
                    product_name=product.name,
                    price=product.price,
                    quantity=item.quantity,
                    total_price=product.price * item.quantity,
                )
            )

        total_price = sum(item.total_price for item in items_read)
        return CartRead(items=items_read, total_price=total_price)

    async def add_to_cart(self, user_id: int, item_create: CartItemCreate) -> CartRead:
        """장바구니에 상품을 추가합니다."""
        async with self.uow:
            product = await self.product_repository.get_by_id(item_create.product_id)
            if not product:
                raise ProductNotFoundException()

            if product.stock < item_create.quantity:
                raise InsufficientStockException()

            existing_item = await self.cart_repository.get_by_user_and_product(user_id, item_create.product_id)

            if existing_item:
                # 도메인 메서드 사용
                try:
                    existing_item.add_quantity(item_create.quantity)
                except InvalidDomainException:
                    pass  # 0 이하 추가는 DTO validation에서 막히므로 여기서는 무시 가능하거나 에러 처리

                await self.cart_repository.save(existing_item)
            else:
                new_item = CartItem(
                    user_id=user_id,
                    product_id=item_create.product_id,
                    quantity=item_create.quantity,
                )
                await self.cart_repository.save(new_item)

        return await self.get_cart(user_id)

    async def update_item_quantity(self, user_id: int, product_id: int, item_update: CartItemUpdate) -> CartRead:
        """장바구니 항목의 수량을 변경합니다."""
        async with self.uow:
            item = await self.cart_repository.get_by_user_and_product(user_id, product_id)
            if not item:
                raise CartItemNotFoundException()

            product = await self.product_repository.get_by_id(product_id)
            if not product:
                raise ProductNotFoundException()

            if product.stock < item_update.quantity:
                raise InsufficientStockException()

            # 도메인 메서드 사용
            try:
                item.update_quantity(item_update.quantity)
            except InvalidDomainException:
                # DTO Validation이 먼저 처리되겠지만, 안전장치
                pass

            await self.cart_repository.save(item)

        return await self.get_cart(user_id)

    async def remove_item(self, user_id: int, product_id: int) -> CartRead:
        """장바구니에서 상품을 제거합니다."""
        async with self.uow:
            item = await self.cart_repository.get_by_user_and_product(user_id, product_id)
            if not item:
                raise CartItemNotFoundException()

            await self.cart_repository.delete(item)

        return await self.get_cart(user_id)
