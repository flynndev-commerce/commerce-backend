import httpx
import pytest
from fastapi import FastAPI
from starlette import status

from app.application.dto.cart_dto import CartRead
from app.application.dto.response import BaseResponse
from app.core.route_names import RouteName
from tests.integration.v1.carts.helpers import TEST_CART_ITEM_QUANTITY, TEST_CART_ITEM_QUANTITY_EXCESSIVE
from tests.integration.v1.products.helpers import create_test_product
from tests.integration.v1.users.helpers import create_test_user, login_and_get_token


@pytest.mark.asyncio
class TestAddItem:
    async def test_add_item_to_cart(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        # Given
        await create_test_user(test_app, client)
        token = await login_and_get_token(test_app, client)
        headers = {"Authorization": f"Bearer {token}"}
        product = await create_test_product(test_app, client)

        # When
        response = await client.post(
            test_app.url_path_for(RouteName.CARTS_ADD_ITEM),
            headers=headers,
            json={
                "productId": product.id,
                "quantity": TEST_CART_ITEM_QUANTITY,
            },
        )

        # Then
        assert response.status_code == status.HTTP_201_CREATED
        response_model = BaseResponse[CartRead].model_validate(response.json())
        assert len(response_model.result.items) == 1
        assert response_model.result.items[0].product_id == product.id
        assert response_model.result.items[0].quantity == TEST_CART_ITEM_QUANTITY
        assert response_model.result.total_price == product.price * TEST_CART_ITEM_QUANTITY

    async def test_add_item_insufficient_stock(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        # Given
        await create_test_user(test_app, client)
        token = await login_and_get_token(test_app, client)
        headers = {"Authorization": f"Bearer {token}"}
        product = await create_test_product(test_app, client)

        # When
        response = await client.post(
            test_app.url_path_for(RouteName.CARTS_ADD_ITEM),
            headers=headers,
            json={
                "productId": product.id,
                "quantity": TEST_CART_ITEM_QUANTITY_EXCESSIVE,
            },
        )

        # Then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
