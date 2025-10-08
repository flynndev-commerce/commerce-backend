import bcrypt
from fastapi import HTTPException, status

from app.domain.user import UserEntity
from app.repositories.user_repository import UserRepository
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

        hashed_password = bcrypt.hashpw(user_create.password.encode("utf-8"), bcrypt.gensalt())
        return await self.user_repository.create(
            user_create=user_create,
            hashed_password=hashed_password.decode("utf-8"),
        )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
