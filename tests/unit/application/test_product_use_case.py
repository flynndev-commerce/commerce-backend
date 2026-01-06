import pytest

from app.application.dto.product_dto import ProductCreate
from app.application.use_cases.product_use_case import ProductUseCase
from app.core.exceptions import ProductNotFoundException
from tests.fakes.fake_unit_of_work import FakeUnitOfWork
from tests.fakes.repositories.fake_product_repository import FakeProductRepository


@pytest.mark.asyncio
class TestProductUseCase:
    async def test_create_product_success(self) -> None:
        # Given
        product_repo = FakeProductRepository()
        uow = FakeUnitOfWork()
        use_case = ProductUseCase(product_repository=product_repo, uow=uow)

        seller_id = 1
        product_create = ProductCreate(name="Test Product", description="Test Description", price=10000, stock=10)

        # When
        result = await use_case.create_product(seller_id, product_create)

        # Then
        assert result.id is not None
        assert result.name == "Test Product"
        assert result.seller_id == seller_id

        # Verify repository
        saved_product = await product_repo.get_by_id(result.id)
        assert saved_product is not None
        assert saved_product.name == "Test Product"

    async def test_get_product_by_id_success(self) -> None:
        # Given
        product_repo = FakeProductRepository()
        uow = FakeUnitOfWork()
        use_case = ProductUseCase(product_repository=product_repo, uow=uow)

        # Create product to retrieve
        seller_id = 1
        product_create = ProductCreate(name="Target Product", description="Desc", price=5000, stock=5)
        created_product = await use_case.create_product(seller_id, product_create)

        # When
        result = await use_case.get_product_by_id(created_product.id)

        # Then
        assert result.id == created_product.id
        assert result.name == "Target Product"

    async def test_get_product_by_id_not_found(self) -> None:
        # Given
        product_repo = FakeProductRepository()
        uow = FakeUnitOfWork()
        use_case = ProductUseCase(product_repository=product_repo, uow=uow)

        # When & Then
        with pytest.raises(ProductNotFoundException):
            await use_case.get_product_by_id(999)
