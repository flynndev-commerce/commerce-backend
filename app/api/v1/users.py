
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from app.containers import Container
from app.domain.user import User
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
@inject
def create_user(
    user_create: UserCreate,
    user_service: Annotated[UserService, Depends(Provide[Container.user_service])],
) -> User:
    """
    새로운 사용자를 생성합니다.
    """
    return user_service.create_user(user_create=user_create)
