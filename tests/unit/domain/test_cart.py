import pytest

from app.domain.exceptions import InvalidDomainException
from app.domain.model.cart import CartItem


class TestCartItem:
    def test_add_quantity_success(self) -> None:
        """수량을 성공적으로 증가시킵니다."""
        # Given
        initial_quantity = 1
        added_quantity = 2
        expected_quantity = initial_quantity + added_quantity
        cart_item = CartItem(user_id=1, product_id=100, quantity=initial_quantity)

        # When
        cart_item.add_quantity(added_quantity)

        # Then
        assert cart_item.quantity == expected_quantity

    def test_add_quantity_invalid_amount(self) -> None:
        """0 이하의 수량을 추가하려고 하면 예외가 발생합니다."""
        # Given
        cart_item = CartItem(user_id=1, product_id=100, quantity=1)

        # When & Then
        with pytest.raises(InvalidDomainException):
            cart_item.add_quantity(0)

        with pytest.raises(InvalidDomainException):
            cart_item.add_quantity(-1)

    def test_update_quantity_success(self) -> None:
        """수량을 성공적으로 변경합니다."""
        # Given
        new_quantity = 5
        cart_item = CartItem(user_id=1, product_id=100, quantity=1)

        # When
        cart_item.update_quantity(new_quantity)

        # Then
        assert cart_item.quantity == new_quantity

    def test_update_quantity_invalid_amount(self) -> None:
        """0 이하로 수량을 변경하려고 하면 예외가 발생합니다."""
        # Given
        cart_item = CartItem(user_id=1, product_id=100, quantity=1)

        # When & Then
        with pytest.raises(InvalidDomainException):
            cart_item.update_quantity(0)

        with pytest.raises(InvalidDomainException):
            cart_item.update_quantity(-5)
