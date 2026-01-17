# 도메인/유즈케이스 기반 테스트 계정 fixture
import os
from collections.abc import AsyncGenerator, Generator
from typing import cast
from unittest.mock import patch

import pytest
import pytest_asyncio
from dependency_injector import providers
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.application.dto.seller_dto import SellerCreate, SellerRead
from app.application.dto.user_dto import UserCreate, UserRead
from app.application.use_cases.seller_use_case import SellerUseCase
from app.application.use_cases.user_use_case import UserUseCase
from app.core.config import Settings
from app.core.db import get_session
from app.core.types import AppWithContainer
from app.main import app

TEST_USER_EMAIL = "testuser@example.com"
TEST_USER_PASSWORD = "testpassword123"
TEST_USER_FULLNAME = "테스트 사용자"
TEST_SELLER_EMAIL = "testseller@example.com"
TEST_SELLER_PASSWORD = "testpassword456"
TEST_SELLER_FULLNAME = "테스트 판매자"
TEST_STORE_NAME = "테스트상점"
TEST_STORE_DESC = "테스트 상점 설명"


# 테스트용 유저/판매자 fixture (직접 생성 금지, 유즈케이스 활용)
@pytest_asyncio.fixture(scope="function")
async def test_user(test_app: FastAPI) -> UserRead:
    """
    유즈케이스를 통해 테스트용 유저를 생성합니다.
    """
    container = cast(AppWithContainer, test_app).container
    async with container.db_session():
        user_use_case: UserUseCase = container.user_use_case()
        user_create = UserCreate(email="user@example.com", password="pw1234", full_name="테스트유저")
        user = await user_use_case.create_user(user_create)
        return user


@pytest_asyncio.fixture(scope="function")
async def test_seller(test_app: FastAPI, test_user: UserRead) -> SellerRead:
    """
    유저를 선행 생성 후, 유즈케이스를 통해 판매자를 등록합니다.
    """
    container = cast(AppWithContainer, test_app).container
    async with container.db_session():
        seller_use_case: SellerUseCase = container.seller_use_case()
        seller_create = SellerCreate(store_name="테스트상점", description="테스트상점설명")
        seller = await seller_use_case.register_seller(test_user.id, seller_create)
        return seller


@pytest.fixture(scope="session", autouse=True)
def mock_bcrypt_speedup() -> Generator[None]:
    """
    테스트 속도 향상을 위해 bcrypt 해싱을 가짜로 대체합니다.
    """
    with patch("bcrypt.gensalt", return_value=b"$2b$04$test_salt_string_vals"):
        with patch("bcrypt.hashpw") as mock_hashpw:
            # 단순 문자열 결합으로 해싱 흉내
            def fake_hashpw(password: bytes, salt: bytes) -> bytes:
                return b"hashed_" + password

            mock_hashpw.side_effect = fake_hashpw

            with patch("bcrypt.checkpw") as mock_checkpw:

                def fake_checkpw(password: bytes, hashed_password: bytes) -> bool:
                    return hashed_password == b"hashed_" + password

                mock_checkpw.side_effect = fake_checkpw
                yield


@pytest.fixture(scope="function")
def test_app() -> FastAPI:
    """
    테스트용 FastAPI 앱 인스턴스를 반환합니다.
    """
    return app


# =============================
# 테스트 환경에서 DB URL 등 주요 설정 오버라이드 예시
# =============================


@pytest_asyncio.fixture(scope="function")
async def client(test_app: FastAPI) -> AsyncGenerator[AsyncClient]:
    """
    테스트용 FastAPI 클라이언트를 생성합니다. (Async)
    각 테스트마다 새로운 인메모리 데이터베이스를 사용합니다.

    아래 3가지 방법 중 하나로 DB URL 등 주요 설정을 오버라이드할 수 있습니다.
    1. 환경변수 patch (os.environ)
    2. settings 객체 patch (unittest.mock.patch)
    3. DI 컨테이너 provider override
    """

    # 1. 환경변수 patch 예시 (Settings는 env_file/.env 및 환경변수 우선)
    with patch.dict(os.environ, {"DATABASE_URL": "sqlite+aiosqlite:///:memory:"}):
        # 2. settings 객체 patch 예시 (get_settings 반환값 patch)
        with patch("app.core.config.get_settings") as mock_get_settings:
            # 기존 settings를 복사하여 DB URL만 변경
            test_settings = Settings()
            test_settings.database_url = "sqlite+aiosqlite:///:memory:"
            mock_get_settings.return_value = test_settings

            # 3. DI 컨테이너 provider override 예시 (필요시)
            if hasattr(test_app, "container"):
                cast(AppWithContainer, test_app).container.settings.override(providers.Singleton(lambda: test_settings))

            # 테스트용 인메모리 데이터베이스 엔진 생성
            test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

            # 테이블 생성 (테스트 시작 전 1회 실행)
            async with test_engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)

            async def override_get_session() -> AsyncGenerator[AsyncSession]:
                # 세션 제공
                async with AsyncSession(test_engine) as session:
                    yield session

            test_app.dependency_overrides[get_session] = override_get_session

            if hasattr(test_app, "container"):
                cast(AppWithContainer, test_app).container.db_session.override(providers.Resource(override_get_session))

            async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as test_client:
                yield test_client

            # 정리: DI 컨테이너/오버라이드 리셋
            if hasattr(test_app, "container"):
                cast(AppWithContainer, test_app).container.db_session.reset_override()
                cast(AppWithContainer, test_app).container.settings.reset_override()
            test_app.dependency_overrides.clear()
