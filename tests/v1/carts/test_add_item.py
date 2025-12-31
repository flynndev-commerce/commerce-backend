from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette import status

from app.application.dto.cart_dto import CartRead
from app.application.dto.response import BaseResponse
from app.core.route_names import RouteName
from tests.v1.carts.helpers import TEST_CART_ITEM_QUANTITY, TEST_CART_ITEM_QUANTITY_EXCESSIVE
from tests.v1.products.helpers import create_test_product
from tests.v1.users.helpers import create_test_user, login_and_get_token


class TestAddItem:
    def test_add_item_to_cart(self, test_app: FastAPI, client: TestClient) -> None:
        # Given
        create_test_user(test_app, client)
        token = login_and_get_token(test_app, client)
        headers = {"Authorization": f"Bearer {token}"}
        product = create_test_product(test_app, client)

        # When
        response = client.post(
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

    def test_add_item_insufficient_stock(self, test_app: FastAPI, client: TestClient) -> None:
        # Given
        create_test_user(test_app, client)
        token = login_and_get_token(test_app, client)
        headers = {"Authorization": f"Bearer {token}"}
        product = create_test_product(test_app, client)

        # When
        response = client.post(
            test_app.url_path_for(RouteName.CARTS_ADD_ITEM),
            headers=headers,
            json={
                "productId": product.id,
                "quantity": TEST_CART_ITEM_QUANTITY_EXCESSIVE,
            },
        )

        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
