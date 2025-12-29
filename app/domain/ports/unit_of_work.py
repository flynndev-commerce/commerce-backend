from abc import ABC, abstractmethod
from typing import Self


class IUnitOfWork(ABC):
    """Unit of Work 인터페이스"""

    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(self, exc_type: type | None, exc_value: Exception | None, traceback: object | None) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...
