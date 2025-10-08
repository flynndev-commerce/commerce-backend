import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import CustomException, ExceptionCode
from app.schemas.response import BaseResponse

logger = logging.getLogger(__name__)


def configure_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException) -> JSONResponse:
        logger.error(f"CustomException: {exc.code} - {exc.message}", exc_info=True)
        return JSONResponse(
            status_code=exc.status_code,
            content=BaseResponse[Any](
                code=exc.code,
                message=exc.message,
                result=exc.data,
            ).model_dump(by_alias=True),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        logger.error(f"StarletteHTTPException: {exc.status_code} - {exc.detail}", exc_info=True)
        return JSONResponse(
            status_code=exc.status_code,
            content=BaseResponse[Any](
                code=ExceptionCode.BAD_REQUEST,
                message=exc.detail,
                result=None,
            ).model_dump(by_alias=True),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.error(f"RequestValidationError: 422 - {exc.errors()}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=BaseResponse[Any](
                code=ExceptionCode.VALIDATION_ERROR,
                message="Validation Error",
                result=exc.errors(),
            ).model_dump(by_alias=True),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Unhandled Exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=BaseResponse[Any](
                code=ExceptionCode.INTERNAL_SERVER_ERROR,
                message="Internal Server Error",
                result=None,
            ).model_dump(by_alias=True),
        )
