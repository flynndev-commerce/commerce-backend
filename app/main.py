from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import users as v1_users
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

    app.include_router(v1_users.router, prefix="/api/v1")

    @app.get("/")
    def read_root() -> dict[str, str]:
        return {"Hello": "World"}

    return app


app = create_app()
