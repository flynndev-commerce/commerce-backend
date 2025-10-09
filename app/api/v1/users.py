from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from app.containers import Container
from app.schemas.response import BaseResponse, Token
from app.schemas.user import UserCreate, UserLogin, UserRead
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=BaseResponse[UserRead],
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_user(
    user_create: UserCreate,
    user_service: Annotated[UserService, Depends(Provide[Container.user_service])],
) -> BaseResponse[UserRead]:
    """
    새로운 사용자를 생성합니다.
    """
    db_user = await user_service.create_user(user_create=user_create)
    user_read = UserRead.model_validate(db_user, from_attributes=True)
    return BaseResponse(result=user_read)


@router.post(
    "/login",
    response_model=BaseResponse[Token],
    status_code=status.HTTP_200_OK,
)
@inject
async def login_for_access_token(
    user_login: UserLogin,
    user_service: Annotated[UserService, Depends(Provide[Container.user_service])],
) -> BaseResponse[Token]:
    """
    사용자 로그인을 처리하고 액세스 토큰을 반환합니다.
    """
    access_token = await user_service.login_user(user_login.email, user_login.password)
    return BaseResponse(result=Token(access_token=access_token))
