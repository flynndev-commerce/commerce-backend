import pytest
from fastapi.testclient import TestClient
from starlette import status


class TestUserCreate:
    """사용자 생성 테스트"""

    def test_create_user_success(self, client: TestClient) -> None:
        """사용자 생성 성공 테스트"""
        response = client.post(
            "/api/v1/users",
            json={
                "email": "test@example.com",
                "password": "password123",
                "fullName": "Test User",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["code"] == "OK"
        assert data["result"]["email"] == "test@example.com"
        assert data["result"]["fullName"] == "Test User"
        assert data["result"]["isActive"] is True
        assert "id" in data["result"]

    def test_create_user_duplicate_email(self, client: TestClient) -> None:
        """중복 이메일로 사용자 생성 실패 테스트"""
        # 첫 번째 사용자 생성
        client.post(
            "/api/v1/users",
            json={
                "email": "test@example.com",
                "password": "password123",
                "fullName": "Test User",
            },
        )

        # 같은 이메일로 두 번째 사용자 생성 시도
        response = client.post(
            "/api/v1/users",
            json={
                "email": "test@example.com",
                "password": "password456",
                "fullName": "Another User",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["code"] == "BAD_REQUEST"
        assert "already registered" in data["message"].lower()

    def test_create_user_invalid_email(self, client: TestClient) -> None:
        """잘못된 이메일 형식으로 사용자 생성 실패 테스트"""
        response = client.post(
            "/api/v1/users",
            json={
                "email": "invalid-email",
                "password": "password123",
                "fullName": "Test User",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_user_short_password(self, client: TestClient) -> None:
        """짧은 비밀번호로 사용자 생성 실패 테스트"""
        response = client.post(
            "/api/v1/users",
            json={
                "email": "test@example.com",
                "password": "short",
                "fullName": "Test User",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """사용자 로그인 테스트"""

    def test_login_success(self, client: TestClient) -> None:
        """로그인 성공 테스트"""
        # 사용자 생성
        client.post(
            "/api/v1/users",
            json={
                "email": "test@example.com",
                "password": "password123",
                "fullName": "Test User",
            },
        )

        # 로그인
        response = client.post(
            "/api/v1/users/login",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == "OK"
        assert "accessToken" in data["result"]
        assert data["result"]["tokenType"] == "bearer"

    def test_login_wrong_password(self, client: TestClient) -> None:
        """잘못된 비밀번호로 로그인 실패 테스트"""
        # 사용자 생성
        client.post(
            "/api/v1/users",
            json={
                "email": "test@example.com",
                "password": "password123",
                "fullName": "Test User",
            },
        )

        # 잘못된 비밀번호로 로그인 시도
        response = client.post(
            "/api/v1/users/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["code"] == "BAD_REQUEST"

    def test_login_nonexistent_user(self, client: TestClient) -> None:
        """존재하지 않는 사용자로 로그인 실패 테스트"""
        response = client.post(
            "/api/v1/users/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserProfile:
    """사용자 프로필 관련 테스트"""

    @pytest.fixture
    def auth_headers(self, client: TestClient) -> dict[str, str]:
        """인증 헤더를 생성하는 fixture"""
        # 사용자 생성
        client.post(
            "/api/v1/users",
            json={
                "email": "test@example.com",
                "password": "password123",
                "fullName": "Test User",
            },
        )

        # 로그인하여 토큰 받기
        response = client.post(
            "/api/v1/users/login",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )
        token = response.json()["result"]["accessToken"]
        return {"Authorization": f"Bearer {token}"}

    def test_get_current_user_success(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """현재 사용자 정보 조회 성공 테스트"""
        response = client.get("/api/v1/users/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == "OK"
        assert data["result"]["email"] == "test@example.com"
        assert data["result"]["fullName"] == "Test User"

    def test_get_current_user_without_auth(self, client: TestClient) -> None:
        """인증 없이 현재 사용자 정보 조회 실패 테스트"""
        response = client.get("/api/v1/users/me")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_user_full_name(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """사용자 이름 수정 성공 테스트"""
        response = client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"fullName": "Updated Name"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == "OK"
        assert data["result"]["fullName"] == "Updated Name"
        assert data["result"]["email"] == "test@example.com"

    def test_update_user_password(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """사용자 비밀번호 수정 성공 테스트"""
        # 비밀번호 변경
        response = client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"password": "newpassword456"},
        )

        assert response.status_code == status.HTTP_200_OK

        # 새 비밀번호로 로그인 시도
        login_response = client.post(
            "/api/v1/users/login",
            json={
                "email": "test@example.com",
                "password": "newpassword456",
            },
        )

        assert login_response.status_code == status.HTTP_200_OK

    def test_update_user_without_auth(self, client: TestClient) -> None:
        """인증 없이 사용자 정보 수정 실패 테스트"""
        response = client.patch(
            "/api/v1/users/me",
            json={"fullName": "Hacker"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
