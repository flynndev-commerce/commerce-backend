from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette import status

from app.application.dto.product_dto import ProductRead
from app.application.dto.response import BaseResponse
from app.core.route_names import RouteName
from tests.v1.products.helpers import (
    TEST_PRODUCT_DESCRIPTION,
    TEST_PRODUCT_NAME,
    TEST_PRODUCT_PRICE,
    TEST_PRODUCT_STOCK,
    create_test_product,
)

TEST_PRODUCT_COUNT_SMALL = 2
TEST_PRODUCT_COUNT_TOTAL = 15
TEST_PRODUCT_PAGE_SIZE = 10
TEST_PRODUCT_REMAINING = 5


class TestProductList:
    """상품 목록 조회 테스트"""

    def test_list_products_empty(self, test_app: FastAPI, client: TestClient) -> None:
        """빈 상품 목록 조회 테스트"""
        response = client.get(test_app.url_path_for(RouteName.PRODUCTS_LIST))

        assert response.status_code == status.HTTP_200_OK
        response_model = BaseResponse[list[ProductRead]].model_validate(response.json())
        assert response_model.code == "OK"
        assert len(response_model.result) == 0

    def test_list_products_with_data(self, test_app: FastAPI, client: TestClient) -> None:
        """데이터가 있는 상품 목록 조회 테스트"""
        # 상품 2개 생성
        create_test_product(test_app, client)
        client.post(
            test_app.url_path_for(RouteName.PRODUCTS_CREATE),
            json={
                "name": "Another Product",
                "description": TEST_PRODUCT_DESCRIPTION,
                "price": TEST_PRODUCT_PRICE,
                "stock": TEST_PRODUCT_STOCK,
            },
        )

        response = client.get(test_app.url_path_for(RouteName.PRODUCTS_LIST))

        assert response.status_code == status.HTTP_200_OK
        response_model = BaseResponse[list[ProductRead]].model_validate(response.json())
        assert response_model.code == "OK"
        assert len(response_model.result) == TEST_PRODUCT_COUNT_SMALL

    def test_list_products_pagination(self, test_app: FastAPI, client: TestClient) -> None:
        """상품 목록 페이지네이션 테스트"""
        # 상품 15개 생성
        for i in range(TEST_PRODUCT_COUNT_TOTAL):
            client.post(
                test_app.url_path_for(RouteName.PRODUCTS_CREATE),
                json={
                    "name": f"{TEST_PRODUCT_NAME} {i}",
                    "description": TEST_PRODUCT_DESCRIPTION,
                    "price": TEST_PRODUCT_PRICE,
                    "stock": TEST_PRODUCT_STOCK,
                },
            )

        # 기본 페이지 (10개)
        response = client.get(test_app.url_path_for(RouteName.PRODUCTS_LIST))
        response_model = BaseResponse[list[ProductRead]].model_validate(response.json())
        assert len(response_model.result) == TEST_PRODUCT_PAGE_SIZE

        # 두 번째 페이지 (5개)
        response = client.get(test_app.url_path_for(RouteName.PRODUCTS_LIST), params={"offset": 10, "limit": 10})
        response_model = BaseResponse[list[ProductRead]].model_validate(response.json())
        assert len(response_model.result) == TEST_PRODUCT_REMAINING
