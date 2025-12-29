from collections.abc import AsyncGenerator, Generator

import pytest
from dependency_injector import providers
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import get_session
from app.main import app


@pytest.fixture(scope="function")
def test_app() -> FastAPI:
    """
    테스트용 FastAPI 앱 인스턴스를 반환합니다.
    """
    return app


@pytest.fixture(scope="function")
def client(test_app: FastAPI) -> Generator[TestClient]:
    """
    테스트용 FastAPI 클라이언트를 생성합니다.
    각 테스트마다 새로운 인메모리 데이터베이스를 사용합니다.
    """
    # 테스트용 인메모리 데이터베이스 엔진 생성
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async def override_get_session() -> AsyncGenerator[AsyncSession]:
        # 테이블 생성
        async with test_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        # 세션 제공
        async with AsyncSession(test_engine) as session:
            yield session

    test_app.dependency_overrides[get_session] = override_get_session

    # DI 컨테이너 오버라이드
    if hasattr(test_app, "container"):
        test_app.container.db_session.override(providers.Resource(override_get_session))  # type: ignore

    with TestClient(test_app) as test_client:
        yield test_client

    if hasattr(test_app, "container"):
        test_app.container.db_session.reset_override()  # type: ignore
    test_app.dependency_overrides.clear()
