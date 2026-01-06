from typing import Self

from app.domain.ports.unit_of_work import IUnitOfWork


class FakeUnitOfWork(IUnitOfWork):
    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type: type | None, exc_value: Exception | None, traceback: object | None) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass
