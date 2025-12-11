from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette import status

from app.application.dto.response import BaseResponse
from app.application.dto.token import Token
from app.application.dto.user_dto import UserRead
from app.core.route_names import RouteName

# 테스트 데이터 상수
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "password123"
TEST_USER_FULL_NAME = "Test User"


def create_test_user(test_app: FastAPI, client: TestClient) -> UserRead:
    """테스트용 사용자를 생성하고 UserRead 모델을 반환하는 헬퍼 함수"""
    response = client.post(
        test_app.url_path_for(RouteName.USERS_CREATE_USER),
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "fullName": TEST_USER_FULL_NAME,
        },
    )

    # 이미 존재하는 경우 로그인으로 정보 가져오기
    if response.status_code == status.HTTP_400_BAD_REQUEST:
        login_response = client.post(
            test_app.url_path_for(RouteName.USERS_LOGIN),
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
            },
        )
        # 로그인 성공 후 현재 사용자 정보 조회
        token = BaseResponse[Token].model_validate(login_response.json()).result.access_token
        user_response = client.get(
            test_app.url_path_for(RouteName.USERS_GET_CURRENT_USER),
            headers={"Authorization": f"Bearer {token}"},
        )
        return BaseResponse[UserRead].model_validate(user_response.json()).result

    response_model = BaseResponse[UserRead].model_validate(response.json())
    return response_model.result


def login_and_get_token(test_app: FastAPI, client: TestClient) -> str:
    """로그인하여 토큰을 반환하는 헬퍼 함수"""
    response = client.post(
        test_app.url_path_for(RouteName.USERS_LOGIN),
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
        },
    )
    response_model = BaseResponse[Token].model_validate(response.json())
    return response_model.result.access_token


class TestUserCreate:
    """사용자 생성 테스트"""

    def test_create_user_success(self, test_app: FastAPI, client: TestClient) -> None:
        """사용자 생성 성공 테스트"""
        response = client.post(
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

    def test_create_user_duplicate_email(self, test_app: FastAPI, client: TestClient) -> None:
        """중복 이메일로 사용자 생성 실패 테스트"""
        # 첫 번째 사용자 생성
        create_test_user(test_app, client)

        # 같은 이메일로 두 번째 사용자 생성 시도
        response = client.post(
            test_app.url_path_for(RouteName.USERS_CREATE_USER),
            json={
                "email": TEST_USER_EMAIL,
                "password": "password456",
                "fullName": "Another User",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Pydantic 모델로 오류 응답 검증
        response_model = BaseResponse[None].model_validate(response.json())
        assert response_model.code == "BAD_REQUEST"
        assert response_model.message is not None
        assert "이미 등록된 이메일입니다." in response_model.message

    def test_create_user_invalid_email(self, test_app: FastAPI, client: TestClient) -> None:
        """잘못된 이메일 형식으로 사용자 생성 실패 테스트"""
        response = client.post(
            test_app.url_path_for(RouteName.USERS_CREATE_USER),
            json={
                "email": "invalid-email",
                "password": "password123",
                "fullName": "Test User",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_user_short_password(self, test_app: FastAPI, client: TestClient) -> None:
        """짧은 비밀번호로 사용자 생성 실패 테스트"""
        response = client.post(
            test_app.url_path_for(RouteName.USERS_CREATE_USER),
            json={
                "email": "test@example.com",
                "password": "short",
                "fullName": "Test User",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """사용자 로그인 테스트"""

    def test_login_success(self, test_app: FastAPI, client: TestClient) -> None:
        """로그인 성공 테스트"""
        # 사용자 생성
        create_test_user(test_app, client)

        # 로그인
        response = client.post(
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

    def test_login_wrong_password(self, test_app: FastAPI, client: TestClient) -> None:
        """잘못된 비밀번호로 로그인 실패 테스트"""
        # 사용자 생성
        create_test_user(test_app, client)

        # 잘못된 비밀번호로 로그인 시도
        response = client.post(
            test_app.url_path_for(RouteName.USERS_LOGIN),
            json={
                "email": TEST_USER_EMAIL,
                "password": "wrongpassword",
            },
        )

        # Pydantic 모델로 오류 응답 검증
        response_model = BaseResponse[None].model_validate(response.json())
        assert response_model.code == "BAD_REQUEST"
        assert response_model.message is not None
        assert "이메일 또는 비밀번호가 올바르지 않습니다." in response_model.message

    def test_login_nonexistent_user(self, test_app: FastAPI, client: TestClient) -> None:
        """존재하지 않는 사용자로 로그인 실패 테스트"""
        response = client.post(
            test_app.url_path_for(RouteName.USERS_LOGIN),
            json={
                "email": "nonexistent@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


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
        assert response_model.result.email == "test@example.com"
        assert response_model.result.full_name == "Test User"

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
            json={"fullName": "Updated Name"},
        )

        assert response.status_code == status.HTTP_200_OK

        # Pydantic 모델로 응답 검증
        response_model = BaseResponse[UserRead].model_validate(response.json())
        assert response_model.code == "OK"
        assert response_model.result.full_name == "Updated Name"
        assert response_model.result.email == TEST_USER_EMAIL

    def test_update_user_password(self, test_app: FastAPI, client: TestClient) -> None:
        """사용자 비밀번호 수정 성공 테스트"""
        headers = self.auth_headers(test_app, client)
        new_password = "newpassword456"

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
            json={"fullName": "Hacker"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
