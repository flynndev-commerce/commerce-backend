import pytest

from app.domain.exceptions import InvalidDomainException, PermissionDeniedException
from app.domain.model.order import Order, OrderStatus


class TestOrder:
    def test_verify_owner_success(self) -> None:
        """주문 소유자가 맞으면 아무 일도 일어나지 않습니다."""
        # Given
        order = Order(user_id=1, total_price=10000)

        # When
        order.verify_owner(1)

        # Then
        # No exception raised

    def test_verify_owner_fail(self) -> None:
        """주문 소유자가 아니면 PermissionDeniedException이 발생합니다."""
        # Given
        order = Order(user_id=1, total_price=10000)

        # When & Then
        with pytest.raises(PermissionDeniedException):
            order.verify_owner(2)

    @pytest.mark.parametrize("initial_status", [OrderStatus.PENDING, OrderStatus.PAID])
    def test_cancel_success(self, initial_status: OrderStatus) -> None:
        """PENDING 또는 PAID 상태에서는 주문 취소가 가능합니다."""
        # Given
        order = Order(user_id=1, total_price=10000, status=initial_status)

        # When
        order.cancel()

        # Then
        assert order.status == OrderStatus.CANCELLED

    @pytest.mark.parametrize("initial_status", [OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.CANCELLED])
    def test_cancel_fail(self, initial_status: OrderStatus) -> None:
        """SHIPPED, DELIVERED, CANCELLED 상태에서는 주문 취소가 불가능합니다."""
        # Given
        order = Order(user_id=1, total_price=10000, status=initial_status)

        # When & Then
        with pytest.raises(InvalidDomainException):
            order.cancel()
