import httpx
import pytest
from fastapi import FastAPI
from starlette import status

from app.core.route_names import RouteName
from tests.integration.v1.users.helpers import create_test_user, login_and_get_token


@pytest.mark.asyncio
class TestProductPermission:
    async def test_create_product_forbidden_for_buyer(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        """구매자는 상품을 생성할 수 없어야 함"""
        # Given
        await create_test_user(test_app, client)
        token = await login_and_get_token(test_app, client)
        headers = {"Authorization": f"Bearer {token}"}

        # When
        response = await client.post(
            test_app.url_path_for(RouteName.PRODUCTS_CREATE),
            headers=headers,
            json={
                "name": "Unauthorized Product",
                "description": "Should fail",
                "price": 1000,
                "stock": 10,
            },
        )

        # Then
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_create_product_success_for_seller(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        """판매자는 상품을 생성할 수 있어야 함"""
        # Given
        await create_test_user(test_app, client)
        token = await login_and_get_token(test_app, client)
        headers = {"Authorization": f"Bearer {token}"}

        # Register as seller
        register_response = await client.post(
            test_app.url_path_for(RouteName.USERS_REGISTER_SELLER),
            headers=headers,
            json={
                "storeName": "My Store",
                "description": "Best store ever",
            },
        )
        assert register_response.status_code == status.HTTP_201_CREATED
        assert register_response.json()["result"]["storeName"] == "My Store"

        # When
        response = await client.post(
            test_app.url_path_for(RouteName.PRODUCTS_CREATE),
            headers=headers,
            json={
                "name": "Authorized Product",
                "description": "Should succeed",
                "price": 1000,
                "stock": 10,
            },
        )

        # Then
        assert response.status_code == status.HTTP_201_CREATED
