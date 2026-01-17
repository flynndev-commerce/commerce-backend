import httpx
import pytest
from fastapi import FastAPI
from starlette import status

from app.application.dto.cart_dto import CartRead
from app.application.dto.response import BaseResponse
from app.core.route_names import RouteName
from tests.integration.v1.carts.helpers import (
    TEST_CART_ITEM_QUANTITY_INITIAL,
    TEST_CART_ITEM_QUANTITY_UPDATE,
)
from tests.integration.v1.products.helpers import create_test_product
from tests.integration.v1.users.helpers import create_test_user, login_and_get_token


@pytest.mark.asyncio
class TestUpdateItem:
    async def test_update_cart_item_quantity(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        # Given
        await create_test_user(test_app, client)
        token = await login_and_get_token(test_app, client)
        headers = {"Authorization": f"Bearer {token}"}
        product = await create_test_product(test_app, client)

        # Add item first
        await client.post(
            test_app.url_path_for(RouteName.CARTS_ADD_ITEM),
            headers=headers,
            json={
                "productId": product.id,
                "quantity": TEST_CART_ITEM_QUANTITY_INITIAL,
            },
        )

        # When
        response = await client.patch(
            test_app.url_path_for(RouteName.CARTS_UPDATE_ITEM, product_id=product.id),
            headers=headers,
            json={
                "quantity": TEST_CART_ITEM_QUANTITY_UPDATE,
            },
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        response_model = BaseResponse[CartRead].model_validate(response.json())
        assert len(response_model.result.items) == 1
        assert response_model.result.items[0].quantity == TEST_CART_ITEM_QUANTITY_UPDATE
        assert response_model.result.total_price == product.price * TEST_CART_ITEM_QUANTITY_UPDATE
