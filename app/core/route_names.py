from enum import StrEnum


class RouteName(StrEnum):
    """
    API 라우트 이름을 정의하는 Enum입니다.
    """

    # Users
    USERS_CREATE_USER = "users:create-user"
    USERS_LOGIN = "users:login"
    USERS_GET_CURRENT_USER = "users:get-current-user"
    USERS_UPDATE_CURRENT_USER = "users:update-current-user"

    # Products
    PRODUCTS_CREATE = "products:create-product"
    PRODUCTS_LIST = "products:list-products"
    PRODUCTS_GET = "products:get-product"
    PRODUCTS_UPDATE = "products:update-product"

    # Orders
    ORDERS_CREATE = "orders:create-order"
    ORDERS_LIST = "orders:list-orders"
    ORDERS_GET = "orders:get-order"
    ORDERS_CANCEL = "orders:cancel-order"
