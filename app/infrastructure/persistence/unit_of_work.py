from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.ports.unit_of_work import IUnitOfWork


class SQLAlchemyUnitOfWork(IUnitOfWork):
    """SQLAlchemy 기반 Unit of Work 구현"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        return self

    async def __aexit__(self, exc_type: type | None, exc_value: Exception | None, traceback: object | None) -> None:
        if exc_type:
            await self.rollback()
        else:
            # 컨텍스트 매니저 종료 시 자동 커밋을 할지, 명시적 커밋을 강제할지 결정해야 함.
            # 보통 명시적 커밋을 선호하지만, 편의를 위해 에러가 없으면 커밋하도록 할 수도 있음.
            # 여기서는 명시적 커밋 패턴을 따르되, UseCase에서 commit()을 호출하지 않으면
            # 변경사항이 반영되지 않도록(rollback) 하는 것이 안전함.
            # 하지만 일반적인 `with transaction:` 패턴은 성공 시 커밋임.
            # 여기서는 "에러가 없으면 커밋" 정책을 사용하겠음.
            await self.commit()

        # 세션은 DI 컨테이너가 관리하므로 여기서 닫지 않음 (scoped session 등 고려)
        # 하지만 AsyncSession은 close가 필요할 수 있음.
        # dependency-injector의 Resource로 관리되므로 여기서는 닫지 않음.

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
