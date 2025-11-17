from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from app.containers import Container
from app.core.route_names import RouteName
from app.core.security import get_current_user
from app.domain.user import UserEntity
from app.schemas.response import BaseResponse, Token
from app.schemas.user import UserCreate, UserLogin, UserRead, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=BaseResponse[UserRead],
    status_code=status.HTTP_201_CREATED,
    name=RouteName.USERS_CREATE_USER,
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
    name=RouteName.USERS_LOGIN,
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


@router.get(
    "/me",
    response_model=BaseResponse[UserRead],
    status_code=status.HTTP_200_OK,
    name=RouteName.USERS_GET_CURRENT_USER,
)
async def get_current_user_info(
    current_user: Annotated[UserEntity, Depends(get_current_user)],
) -> BaseResponse[UserRead]:
    """
    현재 인증된 사용자의 정보를 반환합니다.
    """
    user_read = UserRead.model_validate(current_user, from_attributes=True)
    return BaseResponse(result=user_read)


@router.patch(
    "/me",
    response_model=BaseResponse[UserRead],
    status_code=status.HTTP_200_OK,
    name=RouteName.USERS_UPDATE_CURRENT_USER,
)
@inject
async def update_current_user_info(
    user_update: UserUpdate,
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(Provide[Container.user_service])],
) -> BaseResponse[UserRead]:
    """
    현재 인증된 사용자의 정보를 수정합니다.
    """
    updated_user = await user_service.update_user(current_user, user_update)
    user_read = UserRead.model_validate(updated_user, from_attributes=True)
    return BaseResponse(result=user_read)
