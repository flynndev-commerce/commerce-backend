from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.application.dto.order_dto import OrderRead
from app.application.dto.response import BaseResponse
from app.core.route_names import RouteName
from tests.integration.v1.products.helpers import create_test_product
from tests.integration.v1.users.helpers import create_test_user, login_and_get_token

# 테스트 데이터 상수
TEST_ORDER_QUANTITY = 2
TEST_ORDER_QUANTITY_EXCESS = 1000
TEST_ORDER_ID_NONEXISTENT = 99999


def create_test_order(test_app: FastAPI, client: TestClient) -> OrderRead:
    """테스트용 주문을 생성하고 OrderRead 모델을 반환하는 헬퍼 함수"""
    # 사용자 및 상품 생성
    create_test_user(test_app, client)
    product = create_test_product(test_app, client)
    token = login_and_get_token(test_app, client)

    response = client.post(
        test_app.url_path_for(RouteName.ORDERS_CREATE),
        headers={"Authorization": f"Bearer {token}"},
        json={
            "items": [
                {
                    "productId": product.id,
                    "quantity": TEST_ORDER_QUANTITY,
                }
            ]
        },
    )
    response_model = BaseResponse[OrderRead].model_validate(response.json())
    return response_model.result
