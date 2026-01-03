from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette import status

from app.application.dto.product_dto import ProductRead
from app.application.dto.response import BaseResponse
from app.core.route_names import RouteName
from tests.v1.products.helpers import (
    TEST_PRODUCT_DESCRIPTION,
    TEST_PRODUCT_INVALID_PRICE,
    TEST_PRODUCT_INVALID_STOCK,
    TEST_PRODUCT_NAME,
    TEST_PRODUCT_PRICE,
    TEST_PRODUCT_STOCK,
    create_test_seller,
)


class TestProductCreate:
    """상품 생성 테스트"""

    def test_create_product_success(self, test_app: FastAPI, client: TestClient) -> None:
        """상품 생성 성공 테스트"""
        headers = create_test_seller(test_app, client)

        response = client.post(
            test_app.url_path_for(RouteName.PRODUCTS_CREATE),
            headers=headers,
            json={
                "name": TEST_PRODUCT_NAME,
                "description": TEST_PRODUCT_DESCRIPTION,
                "price": TEST_PRODUCT_PRICE,
                "stock": TEST_PRODUCT_STOCK,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED

        response_model = BaseResponse[ProductRead].model_validate(response.json())
        assert response_model.code == "OK"
        assert response_model.result.name == TEST_PRODUCT_NAME
        assert response_model.result.description == TEST_PRODUCT_DESCRIPTION
        assert response_model.result.price == TEST_PRODUCT_PRICE
        assert response_model.result.stock == TEST_PRODUCT_STOCK
        assert response_model.result.id is not None

    def test_create_product_invalid_price(self, test_app: FastAPI, client: TestClient) -> None:
        """유효하지 않은 가격으로 상품 생성 실패 테스트"""
        headers = create_test_seller(test_app, client)

        response = client.post(
            test_app.url_path_for(RouteName.PRODUCTS_CREATE),
            headers=headers,
            json={
                "name": TEST_PRODUCT_NAME,
                "price": TEST_PRODUCT_INVALID_PRICE,  # 잘못된 가격
                "stock": TEST_PRODUCT_STOCK,
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_product_invalid_stock(self, test_app: FastAPI, client: TestClient) -> None:
        """유효하지 않은 재고로 상품 생성 실패 테스트"""
        headers = create_test_seller(test_app, client)

        response = client.post(
            test_app.url_path_for(RouteName.PRODUCTS_CREATE),
            headers=headers,
            json={
                "name": TEST_PRODUCT_NAME,
                "price": TEST_PRODUCT_PRICE,
                "stock": TEST_PRODUCT_INVALID_STOCK,  # 잘못된 재고
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
