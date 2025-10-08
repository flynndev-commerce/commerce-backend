
from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.domain.user import User, UserCreate
from app.repositories.user_repository import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, user_create: UserCreate) -> User:
        db_user = self.user_repository.get_by_email(email=user_create.email)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed_password = pwd_context.hash(user_create.password)
        return self.user_repository.create(user_create=user_create, hashed_password=hashed_password)
