from dependency_injector import containers, providers

from app.application.use_cases.cart_use_case import CartUseCase
from app.application.use_cases.order_use_case import OrderUseCase
from app.application.use_cases.product_use_case import ProductUseCase
from app.application.use_cases.seller_use_case import SellerUseCase
from app.application.use_cases.user_use_case import UserUseCase
from app.core.config import get_settings
from app.core.db import get_session
from app.infrastructure.persistence.cart_repository import SQLCartRepository
from app.infrastructure.persistence.order_repository import SQLOrderRepository
from app.infrastructure.persistence.product_repository import SQLProductRepository
from app.infrastructure.persistence.seller_repository import SQLSellerRepository
from app.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from app.infrastructure.persistence.user_repository import SQLUserRepository


class Container(containers.DeclarativeContainer):
    # Wiring
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.core.security",
            "app.infrastructure.api.v1.users",
            "app.infrastructure.api.v1.products",
            "app.infrastructure.api.v1.orders",
            "app.infrastructure.api.v1.carts",
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
    order_repository = providers.Factory(
        SQLOrderRepository,
        session=db_session,
    )
    cart_repository = providers.Factory(
        SQLCartRepository,
        session=db_session,
    )
    seller_repository = providers.Factory(
        SQLSellerRepository,
        session=db_session,
    )

    # Unit of Work
    uow = providers.Factory(
        SQLAlchemyUnitOfWork,
        session=db_session,
    )

    # Use Cases
    user_use_case = providers.Factory(
        UserUseCase,
        user_repository=user_repository,
        uow=uow,
    )
    product_use_case = providers.Factory(
        ProductUseCase,
        product_repository=product_repository,
        uow=uow,
    )
    order_use_case = providers.Factory(
        OrderUseCase,
        order_repository=order_repository,
        product_repository=product_repository,
        cart_repository=cart_repository,
        uow=uow,
    )
    cart_use_case = providers.Factory(
        CartUseCase,
        cart_repository=cart_repository,
        product_repository=product_repository,
        uow=uow,
    )
    seller_use_case = providers.Factory(
        SellerUseCase,
        seller_repository=seller_repository,
        user_repository=user_repository,
        uow=uow,
    )
