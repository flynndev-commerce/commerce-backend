import httpx
import pytest
from fastapi import FastAPI
from starlette import status

from app.application.dto.response import BaseResponse
from app.application.dto.token import Token
from app.core.route_names import RouteName
from tests.integration.v1.users.helpers import (
    TEST_USER_EMAIL,
    TEST_USER_EMAIL_NONEXISTENT,
    TEST_USER_PASSWORD,
    TEST_USER_PASSWORD_WRONG,
    create_test_user,
)


@pytest.mark.asyncio
class TestUserLogin:
    """사용자 로그인 테스트"""

    async def test_login_success(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        """로그인 성공 테스트"""
        # 사용자 생성
        await create_test_user(test_app, client)

        # 로그인
        response = await client.post(
            test_app.url_path_for(RouteName.USERS_LOGIN),
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
            },
        )

        assert response.status_code == status.HTTP_200_OK

        # Pydantic 모델로 응답 검증
        response_model = BaseResponse[Token].model_validate(response.json())
        assert response_model.code == "OK"
        assert response_model.result.access_token is not None
        assert len(response_model.result.access_token) > 0
        assert response_model.result.token_type == "bearer"

    async def test_login_wrong_password(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        """잘못된 비밀번호로 로그인 실패 테스트"""
        # 사용자 생성
        await create_test_user(test_app, client)

        # 잘못된 비밀번호로 로그인 시도
        response = await client.post(
            test_app.url_path_for(RouteName.USERS_LOGIN),
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD_WRONG,
            },
        )

        # Pydantic 모델로 오류 응답 검증
        response_model = BaseResponse[None].model_validate(response.json())
        assert response_model.code == "UNAUTHORIZED"
        assert response_model.message is not None
        assert "이메일 또는 비밀번호가 올바르지 않습니다." in response_model.message

    async def test_login_nonexistent_user(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        """존재하지 않는 사용자로 로그인 실패 테스트"""
        response = await client.post(
            test_app.url_path_for(RouteName.USERS_LOGIN),
            json={
                "email": TEST_USER_EMAIL_NONEXISTENT,
                "password": TEST_USER_PASSWORD,
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
