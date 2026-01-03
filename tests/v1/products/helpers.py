from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.application.dto.product_dto import ProductRead
from app.application.dto.response import BaseResponse
from app.core.route_names import RouteName

# 테스트 데이터 상수
TEST_PRODUCT_NAME = "테스트 상품"
TEST_PRODUCT_DESCRIPTION = "테스트 상품 설명입니다."
TEST_PRODUCT_PRICE = 10000.0
TEST_PRODUCT_STOCK = 100
TEST_PRODUCT_INVALID_PRICE = -1000.0
TEST_PRODUCT_INVALID_STOCK = -1
TEST_PRODUCT_NAME_UPDATED = "수정된 상품"
TEST_PRODUCT_PRICE_UPDATED = 20000.0
TEST_PRODUCT_ID_NONEXISTENT = 99999


def create_test_product(
    test_app: FastAPI,
    client: TestClient,
    name: str = TEST_PRODUCT_NAME,
    description: str = TEST_PRODUCT_DESCRIPTION,
    price: float = TEST_PRODUCT_PRICE,
    stock: int = TEST_PRODUCT_STOCK,
) -> ProductRead:
    """테스트용 상품을 생성하고 ProductRead 모델을 반환하는 헬퍼 함수"""
    response = client.post(
        test_app.url_path_for(RouteName.PRODUCTS_CREATE),
        json={
            "name": name,
            "description": description,
            "price": price,
            "stock": stock,
        },
    )
    response_model = BaseResponse[ProductRead].model_validate(response.json())
    return response_model.result
