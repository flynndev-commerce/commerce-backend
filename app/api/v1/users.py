from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from app.containers import Container
from app.schemas.response import BaseResponse
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=BaseResponse[UserRead],
    status_code=status.HTTP_201_CREATED,
)
@inject
def create_user(
    user_create: UserCreate,
    user_service: Annotated[UserService, Depends(Provide[Container.user_service])],
) -> BaseResponse[UserRead]:
    """
    새로운 사용자를 생성합니다.
    """
    db_user = user_service.create_user(user_create=user_create)
    user_read = UserRead.model_validate(db_user)
    return BaseResponse(result=user_read)
