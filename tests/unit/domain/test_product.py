import pytest

from app.domain.exceptions import InsufficientStockException, InvalidDomainException, PermissionDeniedException
from app.domain.model.product import Product


class TestProduct:
    def test_decrease_stock_success(self) -> None:
        """재고를 성공적으로 차감합니다."""
        # Given
        initial_stock = 10
        decrease_amount = 3
        expected_stock = initial_stock - decrease_amount
        product = Product(name="Test Product", price=1000, stock=initial_stock, seller_id=1)

        # When
        product.decrease_stock(decrease_amount)

        # Then
        assert product.stock == expected_stock

    def test_decrease_stock_insufficient(self) -> None:
        """재고보다 더 많이 차감하려고 하면 InsufficientStockException이 발생합니다."""
        # Given
        product = Product(name="Test Product", price=1000, stock=10, seller_id=1)

        # When & Then
        with pytest.raises(InsufficientStockException):
            product.decrease_stock(11)

    def test_decrease_stock_invalid_quantity(self) -> None:
        """0 이하의 수량을 차감하려고 하면 InvalidDomainException이 발생합니다."""
        # Given
        product = Product(name="Test Product", price=1000, stock=10, seller_id=1)

        # When & Then
        with pytest.raises(InvalidDomainException):
            product.decrease_stock(0)

        with pytest.raises(InvalidDomainException):
            product.decrease_stock(-1)

    def test_check_stock_success(self) -> None:
        """재고가 충분하면 아무 예외도 발생하지 않습니다."""
        # Given
        product = Product(name="Test Product", price=1000, stock=10, seller_id=1)

        # When
        product.check_stock(10)

        # Then
        # No exception

    def test_check_stock_fail(self) -> None:
        """재고가 부족하면 InsufficientStockException이 발생합니다."""
        # Given
        product = Product(name="Test Product", price=1000, stock=10, seller_id=1)

        # When & Then
        with pytest.raises(InsufficientStockException):
            product.check_stock(11)

    def test_update_price_success(self) -> None:
        """가격을 성공적으로 변경합니다."""
        # Given
        new_price = 2000
        product = Product(name="Test Product", price=1000, stock=10, seller_id=1)

        # When
        product.update_price(new_price)

        # Then
        assert product.price == new_price

    def test_update_price_invalid(self) -> None:
        """0 이하의 가격으로 변경하려고 하면 InvalidDomainException이 발생합니다."""
        # Given
        product = Product(name="Test Product", price=1000, stock=10, seller_id=1)

        # When & Then
        with pytest.raises(InvalidDomainException):
            product.update_price(0)

        with pytest.raises(InvalidDomainException):
            product.update_price(-100)

    def test_add_stock_success(self) -> None:
        """재고를 성공적으로 추가합니다."""
        # Given
        initial_stock = 10
        add_amount = 5
        expected_stock = initial_stock + add_amount
        product = Product(name="Test Product", price=1000, stock=initial_stock, seller_id=1)

        # When
        product.add_stock(add_amount)

        # Then
        assert product.stock == expected_stock

    def test_add_stock_invalid(self) -> None:
        """0 이하의 재고를 추가하려고 하면 InvalidDomainException이 발생합니다."""
        # Given
        product = Product(name="Test Product", price=1000, stock=10, seller_id=1)

        # When & Then
        with pytest.raises(InvalidDomainException):
            product.add_stock(0)

        with pytest.raises(InvalidDomainException):
            product.add_stock(-5)

    def test_verify_owner_success(self) -> None:
        """판매자 본인이면 아무 예외도 발생하지 않습니다."""
        # Given
        product = Product(name="Test Product", price=1000, stock=10, seller_id=1)

        # When
        product.verify_owner(1)

        # Then
        # No exception

    def test_verify_owner_fail(self) -> None:
        """판매자 본인이 아니면 PermissionDeniedException이 발생합니다."""
        # Given
        product = Product(name="Test Product", price=1000, stock=10, seller_id=1)

        # When & Then
        with pytest.raises(PermissionDeniedException):
            product.verify_owner(2)
