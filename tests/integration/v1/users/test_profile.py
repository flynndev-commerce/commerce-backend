from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette import status

from app.application.dto.response import BaseResponse
from app.application.dto.token import Token
from app.application.dto.user_dto import UserRead
from app.core.route_names import RouteName
from tests.integration.v1.users.helpers import (
    TEST_USER_EMAIL,
    TEST_USER_FULL_NAME,
    TEST_USER_FULL_NAME_HACKER,
    TEST_USER_FULL_NAME_UPDATED,
    TEST_USER_PASSWORD_NEW,
    create_test_user,
    login_and_get_token,
)


class TestUserProfile:
    """사용자 프로필 관련 테스트"""

    def auth_headers(self, test_app: FastAPI, client: TestClient) -> dict[str, str]:
        """인증 헤더를 반환하는 헬퍼 메서드"""
        create_test_user(test_app, client)
        token = login_and_get_token(test_app, client)
        return {"Authorization": f"Bearer {token}"}

    def test_get_current_user_success(self, test_app: FastAPI, client: TestClient) -> None:
        """현재 사용자 정보 조회 성공 테스트"""
        headers = self.auth_headers(test_app, client)
        response = client.get(test_app.url_path_for(RouteName.USERS_GET_CURRENT_USER), headers=headers)

        assert response.status_code == status.HTTP_200_OK

        # Pydantic 모델로 응답 검증
        response_model = BaseResponse[UserRead].model_validate(response.json())
        assert response_model.code == "OK"
        assert response_model.result.email == TEST_USER_EMAIL
        assert response_model.result.full_name == TEST_USER_FULL_NAME

    def test_get_current_user_without_auth(self, test_app: FastAPI, client: TestClient) -> None:
        """인증 없이 현재 사용자 정보 조회 실패 테스트"""
        response = client.get(test_app.url_path_for(RouteName.USERS_GET_CURRENT_USER))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_user_full_name(self, test_app: FastAPI, client: TestClient) -> None:
        """사용자 이름 수정 성공 테스트"""
        headers = self.auth_headers(test_app, client)
        response = client.patch(
            test_app.url_path_for(RouteName.USERS_UPDATE_CURRENT_USER),
            headers=headers,
            json={"fullName": TEST_USER_FULL_NAME_UPDATED},
        )

        assert response.status_code == status.HTTP_200_OK

        # Pydantic 모델로 응답 검증
        response_model = BaseResponse[UserRead].model_validate(response.json())
        assert response_model.code == "OK"
        assert response_model.result.full_name == TEST_USER_FULL_NAME_UPDATED
        assert response_model.result.email == TEST_USER_EMAIL

    def test_update_user_password(self, test_app: FastAPI, client: TestClient) -> None:
        """사용자 비밀번호 수정 성공 테스트"""
        headers = self.auth_headers(test_app, client)
        new_password = TEST_USER_PASSWORD_NEW

        # 비밀번호 변경
        response = client.patch(
            test_app.url_path_for(RouteName.USERS_UPDATE_CURRENT_USER),
            headers=headers,
            json={"password": new_password},
        )

        assert response.status_code == status.HTTP_200_OK

        # 새 비밀번호로 로그인 검증
        login_response = client.post(
            test_app.url_path_for(RouteName.USERS_LOGIN),
            json={
                "email": TEST_USER_EMAIL,
                "password": new_password,
            },
        )

        assert login_response.status_code == status.HTTP_200_OK

        # 로그인 응답도 Pydantic으로 검증
        login_model = BaseResponse[Token].model_validate(login_response.json())
        assert login_model.code == "OK"
        assert login_model.result.access_token is not None

    def test_update_user_without_auth(self, test_app: FastAPI, client: TestClient) -> None:
        """인증 없이 사용자 정보 수정 실패 테스트"""
        response = client.patch(
            test_app.url_path_for(RouteName.USERS_UPDATE_CURRENT_USER),
            json={"fullName": TEST_USER_FULL_NAME_HACKER},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
