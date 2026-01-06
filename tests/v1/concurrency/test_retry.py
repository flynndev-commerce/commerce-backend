from typing import Any
from unittest.mock import AsyncMock

import pytest

from app.application.dto.product_dto import ProductUpdate
from app.application.use_cases.order_use_case import OrderUseCase
from app.application.use_cases.product_use_case import ProductUseCase
from app.core.config import get_settings
from app.domain.exceptions import ConcurrentModificationException
from app.domain.model.order import Order, OrderStatus
from app.domain.model.product import Product


@pytest.mark.asyncio
async def test_update_product_retry_success() -> None:
    # Arrange
    mock_repo = AsyncMock()
    mock_uow = AsyncMock()
    mock_uow.__aenter__.return_value = None
    mock_uow.__aexit__.return_value = None

    use_case = ProductUseCase(product_repository=mock_repo, uow=mock_uow)

    item = Product(id=1, seller_id=1, name="Test", description="Desc", price=1000, stock=10, version=1)

    # Mock get_by_id to return the product
    mock_repo.get_by_id.return_value = item

    # Mock update to fail twice then succeed
    exception = ConcurrentModificationException("Conflict")
    mock_repo.update.side_effect = [exception, exception, item]

    # Act
    dto = ProductUpdate(name="Updated")
    await use_case.update_product(seller_id=1, product_id=1, product_update=dto)

    # Assert
    settings = get_settings()
    assert mock_repo.get_by_id.call_count == settings.max_retry_count
    assert mock_repo.update.call_count == settings.max_retry_count


@pytest.mark.asyncio
async def test_update_product_retry_failure_max_retries() -> None:
    # Arrange
    mock_repo = AsyncMock()
    mock_uow = AsyncMock()
    mock_uow.__aenter__.return_value = None
    mock_uow.__aexit__.return_value = None

    use_case = ProductUseCase(product_repository=mock_repo, uow=mock_uow)

    item = Product(id=1, seller_id=1, name="Test", description="Desc", price=1000, stock=10, version=1)

    mock_repo.get_by_id.return_value = item

    settings = get_settings()
    # Mock update to fail always
    exception = ConcurrentModificationException("Conflict")
    # Prepare enough exceptions to fail all retries
    mock_repo.update.side_effect = [exception] * (settings.max_retry_count + 1)

    # Act & Assert
    dto = ProductUpdate(name="Updated")

    with pytest.raises(ConcurrentModificationException):
        await use_case.update_product(seller_id=1, product_id=1, product_update=dto)

    assert mock_repo.get_by_id.call_count == settings.max_retry_count
    assert mock_repo.update.call_count == settings.max_retry_count


@pytest.mark.asyncio
async def test_cancel_order_retry_success() -> None:
    # Arrange
    mock_order_repo = AsyncMock()
    mock_product_repo = AsyncMock()
    mock_cart_repo = AsyncMock()
    mock_uow = AsyncMock()
    mock_uow.__aenter__.return_value = None
    mock_uow.__aexit__.return_value = None

    use_case = OrderUseCase(
        order_repository=mock_order_repo,
        product_repository=mock_product_repo,
        cart_repository=mock_cart_repo,
        uow=mock_uow,
    )

    def get_fresh_order(*args: Any, **kwargs: Any) -> Order:
        return Order(id=1, user_id=1, status=OrderStatus.PENDING, total_price=1000, items=[], version=1)

    # Mock find_by_id to return a fresh order each time
    mock_order_repo.find_by_id.side_effect = get_fresh_order

    # Mock save to fail twice then succeed
    # Note: save returns the updated order. We can check call count.
    exception = ConcurrentModificationException("Conflict")
    # We can assume successful save returns the order
    mock_order_repo.save.side_effect = [exception, exception, get_fresh_order()]

    # Act
    await use_case.cancel_order(user_id=1, order_id=1)

    # Assert
    settings = get_settings()
    assert mock_order_repo.find_by_id.call_count == settings.max_retry_count
    assert mock_order_repo.save.call_count == settings.max_retry_count
