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
