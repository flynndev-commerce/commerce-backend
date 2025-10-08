from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any, cast

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.api.v1 import users as v1_users
from app.containers import Container
from app.core.config import get_settings
from app.core.db import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # 시작 시 실행
    create_db_and_tables()
    yield
    # 종료 시 실행


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": "ERROR",
            "message": exc.detail,
            "result": None,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "ERROR",
            "message": "Internal Server Error",
            "result": None,
        },
    )


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.title,
        version=settings.version,
        debug=settings.debug,
        lifespan=lifespan,
        container=Container(),
    )

    app.add_exception_handler(HTTPException, cast(Callable[[Request, Exception], Any], http_exception_handler))
    app.add_exception_handler(Exception, generic_exception_handler)

    app.include_router(v1_users.router, prefix="/api/v1")

    @app.get("/")
    def read_root() -> dict[str, str]:
        return {"Hello": "World"}

    return app


app = create_app()
