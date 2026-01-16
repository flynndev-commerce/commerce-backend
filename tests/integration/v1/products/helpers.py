import httpx
from fastapi import FastAPI

from app.application.dto.product_dto import ProductRead
from app.application.dto.response import BaseResponse
from app.core.route_names import RouteName
from tests.integration.v1.users.helpers import create_test_user, login_and_get_token

# 테스트 데이터 상수
TEST_SELLER_EMAIL = "seller@example.com"
TEST_SELLER_PASSWORD = "sellerpassword"
TEST_PRODUCT_NAME = "테스트 상품"
TEST_PRODUCT_DESCRIPTION = "테스트 상품 설명입니다."
TEST_PRODUCT_PRICE = 10000.0
TEST_PRODUCT_STOCK = 100
TEST_PRODUCT_INVALID_PRICE = -1000.0
TEST_PRODUCT_INVALID_STOCK = -1
TEST_PRODUCT_NAME_UPDATED = "수정된 상품"
TEST_PRODUCT_PRICE_UPDATED = 20000.0
TEST_PRODUCT_ID_NONEXISTENT = 99999


async def create_test_seller(test_app: FastAPI, client: httpx.AsyncClient) -> dict[str, str]:
    """테스트용 판매자를 생성하고 인증 헤더를 반환합니다."""
    # 판매자 생성 및 로그인
    await create_test_user(test_app, client, email=TEST_SELLER_EMAIL, password=TEST_SELLER_PASSWORD)
    token = await login_and_get_token(test_app, client, email=TEST_SELLER_EMAIL, password=TEST_SELLER_PASSWORD)
    headers = {"Authorization": f"Bearer {token}"}

    # 판매자 등록 (이미 등록된 경우 무시)
    await client.post(
        test_app.url_path_for(RouteName.USERS_REGISTER_SELLER),
        headers=headers,
        json={
            "storeName": "Test Store",
            "description": "Test Store Description",
        },
    )
    return headers


async def create_test_product(  # noqa: PLR0913
    test_app: FastAPI,
    client: httpx.AsyncClient,
    name: str = TEST_PRODUCT_NAME,
    description: str = TEST_PRODUCT_DESCRIPTION,
    price: float = TEST_PRODUCT_PRICE,
    stock: int = TEST_PRODUCT_STOCK,
) -> ProductRead:
    """테스트용 상품을 생성하고 ProductRead 모델을 반환하는 헬퍼 함수"""
    headers = await create_test_seller(test_app, client)

    response = await client.post(
        test_app.url_path_for(RouteName.PRODUCTS_CREATE),
        headers=headers,
        json={
            "name": name,
            "description": description,
            "price": price,
            "stock": stock,
        },
    )
    response_model = BaseResponse[ProductRead].model_validate(response.json())
    return response_model.result
