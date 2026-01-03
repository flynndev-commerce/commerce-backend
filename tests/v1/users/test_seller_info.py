from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette import status

from app.application.dto.response import BaseResponse
from app.application.dto.user_dto import UserRead
from app.core.route_names import RouteName
from tests.v1.users.helpers import create_test_user, login_and_get_token


class TestSellerInfo:
    def test_get_current_user_with_seller_info(self, test_app: FastAPI, client: TestClient) -> None:
        """판매자 등록 후 사용자 정보 조회 시 판매자 정보가 포함되는지 테스트"""
        # 1. Create User & Login
        create_test_user(test_app, client)
        token = login_and_get_token(test_app, client)
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Register as Seller
        seller_data = {"storeName": "My Store", "description": "Best store ever"}
        response = client.post(
            test_app.url_path_for(RouteName.USERS_REGISTER_SELLER), headers=headers, json=seller_data
        )
        assert response.status_code == status.HTTP_201_CREATED

        # 3. Get Current User Info
        response = client.get(test_app.url_path_for(RouteName.USERS_GET_CURRENT_USER), headers=headers)
        assert response.status_code == status.HTTP_200_OK

        # 4. Verify seller_info is present
        response_model = BaseResponse[UserRead].model_validate(response.json())
        assert response_model.result.seller_info is not None
        assert response_model.result.seller_info.store_name == "My Store"
