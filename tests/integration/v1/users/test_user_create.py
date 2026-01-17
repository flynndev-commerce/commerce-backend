import httpx
import pytest
from fastapi import FastAPI
from starlette import status

from app.application.dto.response import BaseResponse
from app.application.dto.user_dto import UserRead
from app.core.route_names import RouteName
from tests.integration.v1.users.helpers import (
    TEST_USER_EMAIL,
    TEST_USER_FULL_NAME,
    TEST_USER_FULL_NAME_ALT,
    TEST_USER_INVALID_EMAIL,
    TEST_USER_PASSWORD,
    TEST_USER_PASSWORD_ALT,
    TEST_USER_PASSWORD_SHORT,
    create_test_user,
)


@pytest.mark.asyncio
class TestUserCreate:
    """사용자 생성 테스트"""

    async def test_create_user_success(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        """사용자 생성 성공 테스트"""
        response = await client.post(
            test_app.url_path_for(RouteName.USERS_CREATE_USER),
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "fullName": TEST_USER_FULL_NAME,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED

        # Pydantic 모델로 응답 검증
        response_model = BaseResponse[UserRead].model_validate(response.json())
        assert response_model.code == "OK"
        assert response_model.result.email == TEST_USER_EMAIL
        assert response_model.result.full_name == TEST_USER_FULL_NAME
        assert response_model.result.is_active is True
        assert response_model.result.id is not None

    async def test_create_user_duplicate_email(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        """중복 이메일로 사용자 생성 실패 테스트"""
        # 첫 번째 사용자 생성
        await create_test_user(test_app, client)

        # 같은 이메일로 두 번째 사용자 생성 시도
        response = await client.post(
            test_app.url_path_for(RouteName.USERS_CREATE_USER),
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD_ALT,
                "fullName": TEST_USER_FULL_NAME_ALT,
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Pydantic 모델로 오류 응답 검증
        response_model = BaseResponse[None].model_validate(response.json())
        assert response_model.code == "EMAIL_ALREADY_EXISTS"
        assert response_model.message is not None
        assert "이미 존재하는 이메일입니다." in response_model.message

    async def test_create_user_invalid_email(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        """잘못된 이메일 형식으로 사용자 생성 실패 테스트"""
        response = await client.post(
            test_app.url_path_for(RouteName.USERS_CREATE_USER),
            json={
                "email": TEST_USER_INVALID_EMAIL,
                "password": TEST_USER_PASSWORD,
                "fullName": TEST_USER_FULL_NAME,
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_user_short_password(self, test_app: FastAPI, client: httpx.AsyncClient) -> None:
        """짧은 비밀번호로 사용자 생성 실패 테스트"""
        response = await client.post(
            test_app.url_path_for(RouteName.USERS_CREATE_USER),
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD_SHORT,
                "fullName": TEST_USER_FULL_NAME,
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
