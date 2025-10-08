from dependency_injector import containers, providers

from app.core.config import get_settings
from app.core.db import get_session
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


class Container(containers.DeclarativeContainer):
    # Wiring
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.v1.users",
        ]
    )

    # Core
    settings = providers.Singleton(get_settings)
    db_session = providers.Resource(get_session)

    # Repositories
    user_repository = providers.Factory(
        UserRepository,
        session=db_session,
    )

    # Services
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
    )
