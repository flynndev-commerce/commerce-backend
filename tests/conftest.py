from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import get_session
from app.main import app


@pytest.fixture(scope="function")
def client() -> Generator[TestClient]:
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

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
