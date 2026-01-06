from app.domain.model.user import User
from app.domain.ports.user_repository import IUserRepository


class FakeUserRepository(IUserRepository):
    def __init__(self) -> None:
        self._data: dict[int, User] = {}
        self._next_id = 1

    async def create(self, user: User) -> User:
        if user.id is None:
            user.id = self._next_id
            self._next_id += 1

        if user.id is not None:
            self._data[user.id] = user
        return user

    async def get_by_email(self, email: str) -> User | None:
        for user in self._data.values():
            if user.email == email:
                return user
        return None

    async def get_by_id(self, user_id: int) -> User | None:
        return self._data.get(user_id)

    async def update(self, user: User) -> User:
        if user.id is not None and user.id in self._data:
            self._data[user.id] = user
        return user
