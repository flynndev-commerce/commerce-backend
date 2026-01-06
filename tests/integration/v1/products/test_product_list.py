from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette import status

from app.application.dto.product_dto import ProductRead
from app.application.dto.response import BaseResponse
from app.core.route_names import RouteName
from tests.integration.v1.products.helpers import (
    TEST_PRODUCT_DESCRIPTION,
    TEST_PRODUCT_NAME,
    TEST_PRODUCT_PRICE,
    TEST_PRODUCT_STOCK,
    create_test_product,
    create_test_seller,
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

        # 두 번째 상품 생성을 위해 헤더 필요 (create_test_product 내부에서 이미 판매자 생성됨)
        # 하지만 create_test_product는 매번 새로운 판매자를 생성하려고 시도할 수 있음 (helpers 구현에 따라)
        # helpers.py의 create_test_seller는 이미 존재하면 로그인만 함.
        # 따라서 create_test_seller를 호출하여 헤더를 얻어옴.
        headers = create_test_seller(test_app, client)

        client.post(
            test_app.url_path_for(RouteName.PRODUCTS_CREATE),
            headers=headers,
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
        headers = create_test_seller(test_app, client)

        # 상품 15개 생성
        for i in range(TEST_PRODUCT_COUNT_TOTAL):
            client.post(
                test_app.url_path_for(RouteName.PRODUCTS_CREATE),
                headers=headers,
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
