from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dto.response import BaseResponse
from app.application.dto.seller_dto import SellerCreate, SellerRead
from app.application.dto.token import Token
from app.application.dto.user_dto import UserCreate, UserLogin, UserRead, UserUpdate
from app.application.use_cases.seller_use_case import SellerUseCase
from app.application.use_cases.user_use_case import UserUseCase
from app.containers import Container
from app.core.route_names import RouteName
from app.core.security import get_current_user
from app.domain.model.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    summary="신규 사용자 생성",
    response_model=BaseResponse[UserRead],
    status_code=status.HTTP_201_CREATED,
    name=RouteName.USERS_CREATE_USER,
)
@inject
async def create_user(
    user_create: UserCreate,
    user_use_case: Annotated[UserUseCase, Depends(Provide[Container.user_use_case])],
) -> BaseResponse[UserRead]:
    """
    새로운 사용자를 생성합니다.
    """
    created_user = await user_use_case.create_user(user_create=user_create)
    return BaseResponse(result=created_user)


@router.post(
    "/login",
    summary="사용자 로그인 (토큰 발급)",
    response_model=BaseResponse[Token],
    status_code=status.HTTP_200_OK,
    name=RouteName.USERS_LOGIN,
)
@inject
async def login_for_access_token(
    user_login: UserLogin,
    user_use_case: Annotated[UserUseCase, Depends(Provide[Container.user_use_case])],
) -> BaseResponse[Token]:
    """
    사용자 로그인을 처리하고 액세스 토큰을 반환합니다.
    """
    access_token = await user_use_case.login_user(user_login.email, user_login.password)
    return BaseResponse(result=Token(access_token=access_token))


@router.get(
    "/me",
    summary="현재 사용자 정보 조회",
    response_model=BaseResponse[UserRead],
    status_code=status.HTTP_200_OK,
    name=RouteName.USERS_GET_CURRENT_USER,
)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> BaseResponse[UserRead]:
    """
    현재 인증된 사용자의 정보를 반환합니다.
    """
    user_read = UserRead.model_validate(current_user)
    return BaseResponse(result=user_read)


@router.patch(
    "/me",
    summary="현재 사용자 정보 수정",
    response_model=BaseResponse[UserRead],
    status_code=status.HTTP_200_OK,
    name=RouteName.USERS_UPDATE_CURRENT_USER,
)
@inject
async def update_current_user_info(
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    user_use_case: Annotated[UserUseCase, Depends(Provide[Container.user_use_case])],
) -> BaseResponse[UserRead]:
    """
    현재 인증된 사용자의 정보를 수정합니다.
    """
    if current_user.id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")

    updated_user = await user_use_case.update_user(current_user.id, user_update)
    return BaseResponse(result=updated_user)


@router.post(
    "/me/seller",
    summary="판매자 등록",
    response_model=BaseResponse[SellerRead],
    status_code=status.HTTP_201_CREATED,
    name=RouteName.USERS_REGISTER_SELLER,
)
@inject
async def register_as_seller(
    seller_create: SellerCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    seller_use_case: Annotated[SellerUseCase, Depends(Provide[Container.seller_use_case])],
) -> BaseResponse[SellerRead]:
    """
    현재 사용자를 판매자로 등록합니다.
    """
    if current_user.id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")

    created_seller = await seller_use_case.register_seller(current_user.id, seller_create)
    return BaseResponse(result=created_seller)
