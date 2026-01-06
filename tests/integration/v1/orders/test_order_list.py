from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette import status

from app.application.dto.order_dto import OrderRead
from app.application.dto.response import BaseResponse
from app.core.route_names import RouteName
from tests.integration.v1.orders.helpers import create_test_order
from tests.integration.v1.users.helpers import login_and_get_token


class TestOrderList:
    """주문 목록 조회 테스트"""

    def test_list_orders_empty(self, test_app: FastAPI, client: TestClient) -> None:
        """빈 주문 목록 조회 테스트"""
        # 사용자 생성 및 로그인 (주문 없음)
        create_test_order(test_app, client)  # 다른 사용자의 주문 생성 (영향 없어야 함)

        # 새로운 사용자 로그인
        client.post(
            test_app.url_path_for(RouteName.USERS_CREATE_USER),
            json={
                "email": "newuser@example.com",
                "password": "password123",
                "fullName": "New User",
            },
        )
        login_response = client.post(
            test_app.url_path_for(RouteName.USERS_LOGIN),
            json={
                "email": "newuser@example.com",
                "password": "password123",
            },
        )
        token = login_response.json()["result"]["accessToken"]

        response = client.get(
            test_app.url_path_for(RouteName.ORDERS_LIST),
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        response_model = BaseResponse[list[OrderRead]].model_validate(response.json())
        assert response_model.code == "OK"
        assert len(response_model.result) == 0

    def test_list_orders_with_data(self, test_app: FastAPI, client: TestClient) -> None:
        """데이터가 있는 주문 목록 조회 테스트"""
        create_test_order(test_app, client)
        token = login_and_get_token(test_app, client)

        response = client.get(
            test_app.url_path_for(RouteName.ORDERS_LIST),
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        response_model = BaseResponse[list[OrderRead]].model_validate(response.json())
        assert response_model.code == "OK"
        assert len(response_model.result) >= 1
