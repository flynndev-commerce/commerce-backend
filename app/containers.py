from dependency_injector import containers, providers

from app.application.use_cases.product_use_case import ProductUseCase
from app.application.use_cases.user_use_case import UserUseCase
from app.core.config import get_settings
from app.core.db import get_session
from app.infrastructure.persistence.product_repository import SQLProductRepository
from app.infrastructure.persistence.user_repository import SQLUserRepository


class Container(containers.DeclarativeContainer):
    # Wiring
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.core.security",
            "app.infrastructure.api.v1.users",
            "app.infrastructure.api.v1.products",
        ]
    )

    # Core
    settings = providers.Singleton(get_settings)
    db_session = providers.Resource(get_session)

    # Repositories
    user_repository = providers.Factory(
        SQLUserRepository,
        session=db_session,
    )
    product_repository = providers.Factory(
        SQLProductRepository,
        session=db_session,
    )

    # Use Cases
    user_use_case = providers.Factory(
        UserUseCase,
        user_repository=user_repository,
    )
    product_use_case = providers.Factory(
        ProductUseCase,
        product_repository=product_repository,
    )
