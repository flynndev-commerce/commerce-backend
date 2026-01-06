from app.application.dto.seller_dto import SellerCreate, SellerRead
from app.core.exceptions import SellerAlreadyExistsException, UserNotFoundException
from app.domain.ports.seller_repository import ISellerRepository
from app.domain.ports.unit_of_work import IUnitOfWork
from app.domain.ports.user_repository import IUserRepository


class SellerUseCase:
    def __init__(
        self,
        seller_repository: ISellerRepository,
        user_repository: IUserRepository,
        uow: IUnitOfWork,
    ):
        self.seller_repository = seller_repository
        self.user_repository = user_repository
        self.uow = uow

    async def register_seller(self, user_id: int, seller_create: SellerCreate) -> SellerRead:
        """사용자를 판매자로 등록합니다."""
        async with self.uow:
            # 1. 사용자 확인
            user = await self.user_repository.get_by_id(user_id=user_id)
            if not user:
                raise UserNotFoundException()

            # 2. 이미 판매자인지 확인
            existing_seller = await self.seller_repository.get_by_user_id(user_id=user_id)
            if existing_seller:
                raise SellerAlreadyExistsException()

            # 3. 판매자 정보 생성
            saved_seller = await self.seller_repository.create(
                user_id=user_id,
                store_name=seller_create.store_name,
                description=seller_create.description,
            )

            # 4. 사용자 역할 업데이트
            user.promote_to_seller()
            await self.user_repository.update(user)

            return SellerRead.model_validate(saved_seller)

    async def get_seller(self, user_id: int) -> SellerRead | None:
        """사용자의 판매자 정보를 조회합니다."""
        seller = await self.seller_repository.get_by_user_id(user_id=user_id)
        if seller:
            return SellerRead.model_validate(seller)
        return None
