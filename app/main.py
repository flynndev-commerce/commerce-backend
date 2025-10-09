from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import configure_routers
from app.containers import Container
from app.core.config import get_settings
from app.core.db import create_db_and_tables
from app.core.exception_handlers import configure_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # 시작 시 실행
    await create_db_and_tables()
    yield
    # 종료 시 실행


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.title,
        version=settings.version,
        debug=settings.debug,
        lifespan=lifespan,
        container=Container(),
    )

    configure_exception_handlers(app)
    configure_routers(app)

    return app


app = create_app()
