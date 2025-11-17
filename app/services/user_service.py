from fastapi import HTTPException, status

from app.core import security
from app.domain.user import UserEntity
from app.repositories.user_repository import UserRepository
from app.schemas.token import TokenPayload
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user(self, user_create: UserCreate) -> UserEntity:
        db_user = await self.user_repository.get_by_email(email=user_create.email)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed_password = security.get_password_hash(user_create.password)
        return await self.user_repository.create(
            user_create=user_create,
            hashed_password=hashed_password,
        )

    async def login_user(self, email: str, password: str) -> str:
        user = await self.user_repository.get_by_email(email=email)
        if not user or not security.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = security.create_access_token(data=TokenPayload(sub=user.email))
        return access_token

    async def update_user(self, user: UserEntity, user_update: UserUpdate) -> UserEntity:
        """
        사용자 정보를 업데이트합니다.

        Args:
            user: 업데이트할 사용자 엔티티
            user_update: 업데이트할 정보

        Returns:
            UserEntity: 업데이트된 사용자 엔티티
        """
        if user_update.full_name is not None:
            user.full_name = user_update.full_name

        if user_update.password is not None:
            user.hashed_password = security.get_password_hash(user_update.password)

        return await self.user_repository.update(user)
