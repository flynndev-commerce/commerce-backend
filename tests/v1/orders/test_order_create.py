from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette import status

from app.application.dto.order_dto import OrderRead
from app.application.dto.response import BaseResponse
from app.core.route_names import RouteName
from app.domain.model.order import OrderStatus
from tests.v1.orders.helpers import TEST_ORDER_QUANTITY, TEST_ORDER_QUANTITY_EXCESS
from tests.v1.products.helpers import TEST_PRODUCT_ID_NONEXISTENT, TEST_PRODUCT_PRICE, create_test_product
from tests.v1.users.helpers import create_test_user, login_and_get_token


class TestOrderCreate:
    """주문 생성 테스트"""

    def test_create_order_success(self, test_app: FastAPI, client: TestClient) -> None:
        """주문 생성 성공 테스트"""
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

        assert response.status_code == status.HTTP_201_CREATED

        response_model = BaseResponse[OrderRead].model_validate(response.json())
        assert response_model.code == "OK"
        assert response_model.result.status == OrderStatus.PENDING
        assert response_model.result.total_price == TEST_PRODUCT_PRICE * TEST_ORDER_QUANTITY
        assert len(response_model.result.items) == 1
        assert response_model.result.items[0].product_id == product.id
        assert response_model.result.items[0].quantity == TEST_ORDER_QUANTITY

    def test_create_order_product_not_found(self, test_app: FastAPI, client: TestClient) -> None:
        """존재하지 않는 상품으로 주문 생성 실패 테스트"""
        create_test_user(test_app, client)
        token = login_and_get_token(test_app, client)

        response = client.post(
            test_app.url_path_for(RouteName.ORDERS_CREATE),
            headers={"Authorization": f"Bearer {token}"},
            json={
                "items": [
                    {
                        "productId": TEST_PRODUCT_ID_NONEXISTENT,
                        "quantity": 1,
                    }
                ]
            },
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_order_insufficient_stock(self, test_app: FastAPI, client: TestClient) -> None:
        """재고 부족으로 주문 생성 실패 테스트"""
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
                        "quantity": TEST_ORDER_QUANTITY_EXCESS,  # 재고보다 많은 수량
                    }
                ]
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
