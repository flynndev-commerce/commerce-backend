import httpx
from fastapi import FastAPI
from starlette import status

from app.application.dto.response import BaseResponse
from app.application.dto.token import Token
from app.application.dto.user_dto import UserRead
from app.core.route_names import RouteName

# 테스트 데이터 상수
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "password123"
TEST_USER_FULL_NAME = "Test User"
TEST_USER_PASSWORD_ALT = "password456"
TEST_USER_FULL_NAME_ALT = "Another User"
TEST_USER_INVALID_EMAIL = "invalid-email"
TEST_USER_PASSWORD_SHORT = "short"
TEST_USER_PASSWORD_WRONG = "wrongpassword"
TEST_USER_EMAIL_NONEXISTENT = "nonexistent@example.com"
TEST_USER_FULL_NAME_UPDATED = "Updated Name"
TEST_USER_PASSWORD_NEW = "newpassword456"
TEST_USER_FULL_NAME_HACKER = "Hacker"


async def create_test_user(
    test_app: FastAPI,
    client: httpx.AsyncClient,
    email: str = TEST_USER_EMAIL,
    password: str = TEST_USER_PASSWORD,
) -> UserRead:
    """테스트용 사용자를 생성하고 UserRead 모델을 반환하는 헬퍼 함수"""
    response = await client.post(
        test_app.url_path_for(RouteName.USERS_CREATE_USER),
        json={
            "email": email,
            "password": password,
            "fullName": TEST_USER_FULL_NAME,
        },
    )

    # 이미 존재하는 경우 로그인으로 정보 가져오기
    if response.status_code == status.HTTP_400_BAD_REQUEST:
        login_response = await client.post(
            test_app.url_path_for(RouteName.USERS_LOGIN),
            json={
                "email": email,
                "password": password,
            },
        )
        # 로그인 성공 후 현재 사용자 정보 조회
        token = BaseResponse[Token].model_validate(login_response.json()).result.access_token
        user_response = await client.get(
            test_app.url_path_for(RouteName.USERS_GET_CURRENT_USER),
            headers={"Authorization": f"Bearer {token}"},
        )
        return BaseResponse[UserRead].model_validate(user_response.json()).result

    response_model = BaseResponse[UserRead].model_validate(response.json())
    return response_model.result


async def login_and_get_token(
    test_app: FastAPI,
    client: httpx.AsyncClient,
    email: str = TEST_USER_EMAIL,
    password: str = TEST_USER_PASSWORD,
) -> str:
    """로그인하여 토큰을 반환하는 헬퍼 함수"""
    response = await client.post(
        test_app.url_path_for(RouteName.USERS_LOGIN),
        json={
            "email": email,
            "password": password,
        },
    )
    response_model = BaseResponse[Token].model_validate(response.json())
    return response_model.result.access_token
