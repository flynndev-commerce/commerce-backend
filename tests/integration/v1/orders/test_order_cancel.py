import httpx
import pytest
from fastapi import FastAPI
from starlette import status

from app.application.dto.order_dto import OrderRead
from app.application.dto.product_dto import ProductRead
from app.application.dto.response import BaseResponse
from app.core.route_names import RouteName
from app.domain.model.order import OrderStatus
from tests.integration.v1.orders.helpers import TEST_ORDER_ID_NONEXISTENT, create_test_order
from tests.integration.v1.products.helpers import TEST_PRODUCT_STOCK
from tests.integration.v1.users.helpers import login_and_get_token


@pytest.mark.asyncio
class TestOrderCancel:
    """주문 취소 테스트"""

    async def test_cancel_order_success(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        """주문 취소 성공 테스트 (상태 변경 및 재고 복구 확인)"""
        order = await create_test_order(test_app, client)
        token = await login_and_get_token(test_app, client)
        product_id = order.items[0].product_id

        # 주문 취소 요청
        response = await client.post(
            test_app.url_path_for(RouteName.ORDERS_CANCEL, order_id=order.id),
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        response_model = BaseResponse[OrderRead].model_validate(response.json())
        assert response_model.code == "OK"
        assert response_model.result.status == OrderStatus.CANCELLED

        # 재고 복구 확인
        product_response = await client.get(
            test_app.url_path_for(RouteName.PRODUCTS_GET, product_id=product_id),
        )
        product_model = BaseResponse[ProductRead].model_validate(product_response.json())
        # 초기 재고로 복구되었는지 확인
        assert product_model.result.stock == TEST_PRODUCT_STOCK

    async def test_cancel_order_not_found(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        """존재하지 않는 주문 취소 실패 테스트"""
        await create_test_order(test_app, client)
        token = await login_and_get_token(test_app, client)

        response = await client.post(
            test_app.url_path_for(RouteName.ORDERS_CANCEL, order_id=TEST_ORDER_ID_NONEXISTENT),
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_cancel_order_forbidden(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        """다른 사용자의 주문 취소 실패 테스트"""
        order = await create_test_order(test_app, client)

        # 다른 사용자 로그인
        await client.post(
            test_app.url_path_for(RouteName.USERS_CREATE_USER),
            json={
                "email": "other@example.com",
                "password": "password123",
                "fullName": "Other User",
            },
        )
        login_response = await client.post(
            test_app.url_path_for(RouteName.USERS_LOGIN),
            json={
                "email": "other@example.com",
                "password": "password123",
            },
        )
        token = login_response.json()["result"]["accessToken"]

        response = await client.post(
            test_app.url_path_for(RouteName.ORDERS_CANCEL, order_id=order.id),
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_cancel_order_invalid_status(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        """이미 취소된 주문 취소 실패 테스트"""
        order = await create_test_order(test_app, client)
        token = await login_and_get_token(test_app, client)

        # 1차 취소 (성공)
        await client.post(
            test_app.url_path_for(RouteName.ORDERS_CANCEL, order_id=order.id),
            headers={"Authorization": f"Bearer {token}"},
        )

        # 2차 취소 (실패)
        response = await client.post(
            test_app.url_path_for(RouteName.ORDERS_CANCEL, order_id=order.id),
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
