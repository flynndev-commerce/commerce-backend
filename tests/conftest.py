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

from app.core.db import get_session
from app.core.types import AppWithContainer
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def mock_bcrypt_speedup() -> Generator[None, None, None]:
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


@pytest_asyncio.fixture(scope="function")
async def client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """
    테스트용 FastAPI 클라이언트를 생성합니다. (Async)
    각 테스트마다 새로운 인메모리 데이터베이스를 사용합니다.
    """
    # 테스트용 인메모리 데이터베이스 엔진 생성
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    # 테이블 생성 (테스트 시작 전 1회 실행)
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        # 세션 제공
        async with AsyncSession(test_engine) as session:
            yield session

    test_app.dependency_overrides[get_session] = override_get_session

    # DI 컨테이너 오버라이드
    if hasattr(test_app, "container"):
        cast(AppWithContainer, test_app).container.db_session.override(providers.Resource(override_get_session))

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as test_client:
        yield test_client

    if hasattr(test_app, "container"):
        cast(AppWithContainer, test_app).container.db_session.reset_override()
    test_app.dependency_overrides.clear()
