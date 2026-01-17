import httpx
import pytest
from fastapi import FastAPI
from starlette import status

from app.application.dto.order_dto import OrderRead
from app.application.dto.response import BaseResponse
from app.core.route_names import RouteName
from tests.integration.v1.orders.helpers import TEST_ORDER_ID_NONEXISTENT, create_test_order
from tests.integration.v1.users.helpers import login_and_get_token


@pytest.mark.asyncio
class TestOrderDetail:
    """주문 상세 조회 테스트"""

    async def test_get_order_success(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        """주문 상세 조회 성공 테스트"""
        order = await create_test_order(test_app, client)
        token = await login_and_get_token(test_app, client)

        response = await client.get(
            test_app.url_path_for(RouteName.ORDERS_GET, order_id=order.id),
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        response_model = BaseResponse[OrderRead].model_validate(response.json())
        assert response_model.code == "OK"
        assert response_model.result.id == order.id
        assert response_model.result.total_price == order.total_price

    async def test_get_order_not_found(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        """존재하지 않는 주문 조회 실패 테스트"""
        await create_test_order(test_app, client)
        token = await login_and_get_token(test_app, client)

        response = await client.get(
            test_app.url_path_for(RouteName.ORDERS_GET, order_id=TEST_ORDER_ID_NONEXISTENT),
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_order_forbidden(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        """다른 사용자의 주문 조회 실패 테스트"""
        # 사용자 A가 주문 생성
        order = await create_test_order(test_app, client)

        # 사용자 B 생성 및 로그인
        await client.post(
            test_app.url_path_for(RouteName.USERS_CREATE_USER),
            json={
                "email": "userb@example.com",
                "password": "password123",
                "fullName": "User B",
            },
        )
        login_response = await client.post(
            test_app.url_path_for(RouteName.USERS_LOGIN),
            json={
                "email": "userb@example.com",
                "password": "password123",
            },
        )
        token_b = login_response.json()["result"]["accessToken"]

        # 사용자 B가 사용자 A의 주문 조회 시도
        response = await client.get(
            test_app.url_path_for(RouteName.ORDERS_GET, order_id=order.id),
            headers={"Authorization": f"Bearer {token_b}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
