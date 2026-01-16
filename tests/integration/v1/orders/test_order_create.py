import httpx
import pytest
from fastapi import FastAPI
from starlette import status

from app.application.dto.order_dto import OrderRead
from app.application.dto.response import BaseResponse
from app.core.route_names import RouteName
from app.domain.model.order import OrderStatus
from tests.integration.v1.carts.helpers import TEST_CART_ITEM_QUANTITY
from tests.integration.v1.orders.helpers import TEST_ORDER_QUANTITY, TEST_ORDER_QUANTITY_EXCESS
from tests.integration.v1.products.helpers import TEST_PRODUCT_ID_NONEXISTENT, TEST_PRODUCT_PRICE, create_test_product
from tests.integration.v1.users.helpers import create_test_user, login_and_get_token


@pytest.mark.asyncio
class TestOrderCreate:
    """주문 생성 테스트"""

    async def test_create_order_success(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        """주문 생성 성공 테스트"""
        # 사용자 및 상품 생성
        await create_test_user(test_app, client)
        product = await create_test_product(test_app, client)
        token = await login_and_get_token(test_app, client)

        response = await client.post(
            test_app.url_path_for(RouteName.ORDERS_CREATE),
            headers={"Authorization": f"Bearer {token}"},
            json={
                "items": [
                    {
                        "productId": product.id,
                        "quantity": TEST_ORDER_QUANTITY,
                    }
                ]
            },
        )

        assert response.status_code == status.HTTP_201_CREATED

        response_model = BaseResponse[OrderRead].model_validate(response.json())
        assert response_model.code == "OK"
        assert response_model.result.status == OrderStatus.PENDING
        assert response_model.result.total_price == TEST_PRODUCT_PRICE * TEST_ORDER_QUANTITY
        assert len(response_model.result.items) == 1
        assert response_model.result.items[0].product_id == product.id
        assert response_model.result.items[0].quantity == TEST_ORDER_QUANTITY

    async def test_create_order_product_not_found(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        """존재하지 않는 상품으로 주문 생성 실패 테스트"""
        await create_test_user(test_app, client)
        token = await login_and_get_token(test_app, client)

        response = await client.post(
            test_app.url_path_for(RouteName.ORDERS_CREATE),
            headers={"Authorization": f"Bearer {token}"},
            json={
                "items": [
                    {
                        "productId": TEST_PRODUCT_ID_NONEXISTENT,
                        "quantity": 1,
                    }
                ]
            },
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_create_order_insufficient_stock(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        """재고 부족으로 주문 생성 실패 테스트"""
        await create_test_user(test_app, client)
        product = await create_test_product(test_app, client)
        token = await login_and_get_token(test_app, client)

        response = await client.post(
            test_app.url_path_for(RouteName.ORDERS_CREATE),
            headers={"Authorization": f"Bearer {token}"},
            json={
                "items": [
                    {
                        "productId": product.id,
                        "quantity": TEST_ORDER_QUANTITY_EXCESS,  # 재고보다 많은 수량
                    }
                ]
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_order_removes_items_from_cart(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        """주문 생성 시 장바구니에 해당 상품이 있다면 제거되는지 테스트"""
        # Given
        await create_test_user(test_app, client)
        token = await login_and_get_token(test_app, client)
        headers = {"Authorization": f"Bearer {token}"}
        product = await create_test_product(test_app, client)

        # 1. 장바구니에 상품 담기
        await client.post(
            test_app.url_path_for(RouteName.CARTS_ADD_ITEM),
            headers=headers,
            json={
                "productId": product.id,
                "quantity": TEST_CART_ITEM_QUANTITY,
            },
        )

        # When
        # 2. 해당 상품 직접 주문
        response = await client.post(
            test_app.url_path_for(RouteName.ORDERS_CREATE),
            headers=headers,
            json={
                "items": [
                    {
                        "productId": product.id,
                        "quantity": 1,
                    }
                ]
            },
        )

        # Then
        assert response.status_code == status.HTTP_201_CREATED

        # 3. 장바구니 확인 (비어있어야 함)
        cart_response = await client.get(
            test_app.url_path_for(RouteName.CARTS_GET_MY_CART),
            headers=headers,
        )
        assert cart_response.status_code == status.HTTP_200_OK
        cart_data = cart_response.json()
        assert len(cart_data["result"]["items"]) == 0

    async def test_create_order_removes_only_ordered_items_from_cart(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        """주문 생성 시 주문한 상품만 장바구니에서 제거되고 나머지는 유지되는지 테스트"""
        # Given
        await create_test_user(test_app, client)
        token = await login_and_get_token(test_app, client)
        headers = {"Authorization": f"Bearer {token}"}

        product1 = await create_test_product(test_app, client, name="Product 1", price=1000)
        product2 = await create_test_product(test_app, client, name="Product 2", price=2000)

        # 1. 장바구니에 두 상품 담기
        await client.post(
            test_app.url_path_for(RouteName.CARTS_ADD_ITEM),
            headers=headers,
            json={"productId": product1.id, "quantity": 1},
        )
        await client.post(
            test_app.url_path_for(RouteName.CARTS_ADD_ITEM),
            headers=headers,
            json={"productId": product2.id, "quantity": 1},
        )

        # When
        # 2. Product 1만 직접 주문
        response = await client.post(
            test_app.url_path_for(RouteName.ORDERS_CREATE),
            headers=headers,
            json={
                "items": [
                    {
                        "productId": product1.id,
                        "quantity": 1,
                    }
                ]
            },
        )

        # Then
        assert response.status_code == status.HTTP_201_CREATED

        # 3. 장바구니 확인 (Product 2만 남아있어야 함)
        cart_response = await client.get(
            test_app.url_path_for(RouteName.CARTS_GET_MY_CART),
            headers=headers,
        )
        assert cart_response.status_code == status.HTTP_200_OK
        cart_data = cart_response.json()
        items = cart_data["result"]["items"]

        assert len(items) == 1
        assert items[0]["productId"] == product2.id
