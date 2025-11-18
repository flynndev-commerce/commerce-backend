from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import get_settings

settings = get_settings()

engine: AsyncEngine = create_async_engine(settings.database_url, echo=True)


async def create_db_and_tables() -> None:
    """
    데이터베이스 테이블을 생성합니다.

    개발 환경에서만 사용하며, 운영 환경에서는 마이그레이션 도구를 사용해야 합니다.
    """
    if not settings.auto_create_tables:
        return

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSession(engine) as session:
        yield session
