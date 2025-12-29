from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.model.user import User
from app.domain.ports.user_repository import IUserRepository
from app.infrastructure.persistence.models.user_entity import UserEntity


class SQLUserRepository(IUserRepository):
    """SQL 데이터베이스에 대한 사용자 리포지토리 구현체"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        db_user = UserEntity.model_validate(user)
        self.session.add(db_user)
        await self.session.flush()
        await self.session.refresh(db_user)
        return User.model_validate(db_user)

    async def get_by_email(self, email: str) -> User | None:
        statement = select(UserEntity).where(UserEntity.email == email)
        result = await self.session.exec(statement)
        db_user = result.first()
        if db_user:
            return User.model_validate(db_user)
        return None

    async def get_by_id(self, user_id: int) -> User | None:
        statement = select(UserEntity).where(UserEntity.id == user_id)
        result = await self.session.exec(statement)
        db_user = result.first()
        if db_user:
            return User.model_validate(db_user)
        return None

    async def update(self, user: User) -> User:
        # UserEntity를 먼저 조회해야 합니다. id가 필수입니다.
        if user.id is None:
            raise ValueError("업데이트를 위해서는 사용자의 ID가 필요합니다.")

        db_user = await self.session.get(UserEntity, user.id)
        if not db_user:
            # 혹은 예외를 발생시킬 수도 있습니다.
            raise ValueError("해당 ID의 사용자를 찾을 수 없습니다.")

        # 받은 user 모델의 값으로 db_user 객체의 값을 업데이트합니다.
        user_data = user.model_dump(exclude_unset=True)
        for key, value in user_data.items():
            setattr(db_user, key, value)

        self.session.add(db_user)
        await self.session.flush()
        await self.session.refresh(db_user)
        return User.model_validate(db_user)
