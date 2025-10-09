from fastapi import HTTPException, status

from app.core import security
from app.domain.user import UserEntity
from app.repositories.user_repository import UserRepository
from app.schemas.token import TokenPayload
from app.schemas.user import UserCreate


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
