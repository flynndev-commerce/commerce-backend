from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.user import UserEntity
from app.schemas.user import UserCreate


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_create: UserCreate, hashed_password: str) -> UserEntity:
        db_user = UserEntity.model_validate(user_create, update={"hashed_password": hashed_password})
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def get_by_email(self, email: str) -> UserEntity | None:
        statement = select(UserEntity).where(UserEntity.email == email)
        return (await self.session.exec(statement)).first()
