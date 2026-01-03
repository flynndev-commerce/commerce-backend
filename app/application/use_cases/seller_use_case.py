from fastapi import HTTPException, status

from app.application.dto.seller_dto import SellerCreate, SellerRead
from app.domain.model.seller import Seller
from app.domain.model.user import UserRole
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
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="사용자를 찾을 수 없습니다.",
                )

            # 2. 이미 판매자인지 확인
            existing_seller = await self.seller_repository.get_by_user_id(user_id=user_id)
            if existing_seller:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 판매자로 등록된 사용자입니다.",
                )

            # 3. 판매자 정보 생성
            seller = Seller(
                user_id=user_id,
                store_name=seller_create.store_name,
                description=seller_create.description,
            )
            saved_seller = await self.seller_repository.save(seller)

            # 4. 사용자 역할 업데이트 (선택 사항: UserRole을 유지한다면)
            if user.role != UserRole.SELLER:
                user.role = UserRole.SELLER
                await self.user_repository.update(user)

            return SellerRead.model_validate(saved_seller)

    async def get_seller(self, user_id: int) -> SellerRead | None:
        """사용자의 판매자 정보를 조회합니다."""
        seller = await self.seller_repository.get_by_user_id(user_id=user_id)
        if seller:
            return SellerRead.model_validate(seller)
        return None
