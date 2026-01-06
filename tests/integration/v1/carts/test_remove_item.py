from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette import status

from app.application.dto.cart_dto import CartRead
from app.application.dto.response import BaseResponse
from app.core.route_names import RouteName
from tests.integration.v1.carts.helpers import TEST_CART_ITEM_QUANTITY_INITIAL
from tests.integration.v1.products.helpers import create_test_product
from tests.integration.v1.users.helpers import create_test_user, login_and_get_token


class TestRemoveItem:
    def test_remove_cart_item(self, test_app: FastAPI, client: TestClient) -> None:
        # Given
        create_test_user(test_app, client)
        token = login_and_get_token(test_app, client)
        headers = {"Authorization": f"Bearer {token}"}
        product = create_test_product(test_app, client)

        # Add item first
        client.post(
            test_app.url_path_for(RouteName.CARTS_ADD_ITEM),
            headers=headers,
            json={
                "productId": product.id,
                "quantity": TEST_CART_ITEM_QUANTITY_INITIAL,
            },
        )

        # When
        response = client.delete(
            test_app.url_path_for(RouteName.CARTS_REMOVE_ITEM, product_id=product.id),
            headers=headers,
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        response_model = BaseResponse[CartRead].model_validate(response.json())
        assert len(response_model.result.items) == 0
        assert response_model.result.total_price == 0.0
