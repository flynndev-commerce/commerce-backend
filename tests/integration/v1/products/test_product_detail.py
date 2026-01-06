from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette import status

from app.application.dto.product_dto import ProductRead
from app.application.dto.response import BaseResponse
from app.core.route_names import RouteName
from tests.integration.v1.products.helpers import (
    TEST_PRODUCT_ID_NONEXISTENT,
    TEST_PRODUCT_NAME,
    TEST_PRODUCT_NAME_UPDATED,
    TEST_PRODUCT_PRICE_UPDATED,
    create_test_product,
    create_test_seller,
)


class TestProductGet:
    """상품 상세 조회 테스트"""

    def test_get_product_success(self, test_app: FastAPI, client: TestClient) -> None:
        """상품 상세 조회 성공 테스트"""
        product = create_test_product(test_app, client)

        response = client.get(
            test_app.url_path_for(RouteName.PRODUCTS_GET, product_id=product.id),
        )

        assert response.status_code == status.HTTP_200_OK
        response_model = BaseResponse[ProductRead].model_validate(response.json())
        assert response_model.code == "OK"
        assert response_model.result.id == product.id
        assert response_model.result.name == TEST_PRODUCT_NAME

    def test_get_product_not_found(self, test_app: FastAPI, client: TestClient) -> None:
        """존재하지 않는 상품 조회 실패 테스트"""
        response = client.get(
            test_app.url_path_for(RouteName.PRODUCTS_GET, product_id=TEST_PRODUCT_ID_NONEXISTENT),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestProductUpdate:
    """상품 수정 테스트"""

    def test_update_product_success(self, test_app: FastAPI, client: TestClient) -> None:
        """상품 수정 성공 테스트"""
        product = create_test_product(test_app, client)
        headers = create_test_seller(test_app, client)

        response = client.patch(
            test_app.url_path_for(RouteName.PRODUCTS_UPDATE, product_id=product.id),
            headers=headers,
            json={
                "name": TEST_PRODUCT_NAME_UPDATED,
                "price": TEST_PRODUCT_PRICE_UPDATED,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        response_model = BaseResponse[ProductRead].model_validate(response.json())
        assert response_model.code == "OK"
        assert response_model.result.name == TEST_PRODUCT_NAME_UPDATED
        assert response_model.result.price == TEST_PRODUCT_PRICE_UPDATED
        # 변경하지 않은 필드는 그대로여야 함
        assert response_model.result.stock == product.stock

    def test_update_product_not_found(self, test_app: FastAPI, client: TestClient) -> None:
        """존재하지 않는 상품 수정 실패 테스트"""
        headers = create_test_seller(test_app, client)

        response = client.patch(
            test_app.url_path_for(RouteName.PRODUCTS_UPDATE, product_id=TEST_PRODUCT_ID_NONEXISTENT),
            headers=headers,
            json={"name": TEST_PRODUCT_NAME_UPDATED},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
