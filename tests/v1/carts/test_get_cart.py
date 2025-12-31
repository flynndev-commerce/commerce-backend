from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette import status

from app.application.dto.cart_dto import CartRead
from app.application.dto.response import BaseResponse
from app.core.route_names import RouteName
from tests.v1.users.helpers import create_test_user, login_and_get_token


class TestGetCart:
    def test_get_empty_cart(self, test_app: FastAPI, client: TestClient) -> None:
        # Given
        create_test_user(test_app, client)
        token = login_and_get_token(test_app, client)
        headers = {"Authorization": f"Bearer {token}"}

        # When
        response = client.get(
            test_app.url_path_for(RouteName.CARTS_GET_MY_CART),
            headers=headers,
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        response_model = BaseResponse[CartRead].model_validate(response.json())
        assert response_model.result.items == []
        assert response_model.result.total_price == 0.0
