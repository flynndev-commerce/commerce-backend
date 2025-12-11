from dependency_injector import containers, providers

from app.application.use_cases.user_use_case import UserUseCase
from app.core.config import get_settings
from app.core.db import get_session
from app.infrastructure.persistence.user_repository import SQLUserRepository


class Container(containers.DeclarativeContainer):
    # Wiring
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.infrastructure.api.v1.users",
            "app.core.security",
        ]
    )

    # Core
    settings = providers.Singleton(get_settings)
    db_session = providers.Resource(get_session)

    # Repositories
    # IUserRepository 포트에 대한 구현체로 SQLUserRepository를 제공
    user_repository = providers.Factory(
        SQLUserRepository,
        session=db_session,
    )

    # Services (Use Cases)
    user_service = providers.Factory(
        UserUseCase,
        user_repository=user_repository,
    )
