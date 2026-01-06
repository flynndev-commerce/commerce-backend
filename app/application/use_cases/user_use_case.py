from app.application.dto.token import TokenPayload
from app.application.dto.user_dto import UserCreate, UserRead, UserUpdate
from app.core import security
from app.core.exceptions import (
    EmailAlreadyExistsException,
    InvalidCredentialsException,
    SellerAlreadyExistsException,
    UserInactiveException,
    UserNotFoundException,
)
from app.domain.model.user import User
from app.domain.ports.unit_of_work import IUnitOfWork
from app.domain.ports.user_repository import IUserRepository


class UserUseCase:
    def __init__(self, user_repository: IUserRepository, uow: IUnitOfWork):
        self.user_repository = user_repository
        self.uow = uow

    async def create_user(self, user_create: UserCreate) -> UserRead:
        async with self.uow:
            existing_user = await self.user_repository.get_by_email(email=user_create.email)
            if existing_user:
                raise EmailAlreadyExistsException()

            # 도메인 모델 생성 및 비밀번호 설정
            # Pydantic 모델이라 필드가 필수이므로 임시 값으로 생성 후 설정
            user_to_create = User(
                email=user_create.email,
                full_name=user_create.full_name,
                hashed_password="temp",  # set_password로 덮어씌워짐
                is_active=True,
            )
            user_to_create.set_password(user_create.password)

            created_user = await self.user_repository.create(user=user_to_create)

            return UserRead.model_validate(created_user)

    async def login_user(self, email: str, password: str) -> str:
        user = await self.user_repository.get_by_email(email=email)

        # 도메인 메서드 사용
        if not user or not user.verify_password(password):
            raise InvalidCredentialsException()

        if not user.is_active:
            raise UserInactiveException()

        access_token = security.create_access_token(data=TokenPayload(sub=user.email))
        return access_token

    async def get_user_by_id(self, user_id: int) -> UserRead | None:
        user = await self.user_repository.get_by_id(user_id=user_id)
        if user:
            return UserRead.model_validate(user)
        return None

    async def update_user(self, user_id: int, user_update: UserUpdate) -> UserRead:
        async with self.uow:
            user_to_update = await self.user_repository.get_by_id(user_id=user_id)
            if not user_to_update:
                raise UserNotFoundException()

            update_data = user_update.model_dump(exclude_unset=True)

            # 비밀번호 업데이트가 있는 경우 도메인 메서드 사용
            password = update_data.pop("password", None)

            # 비밀번호 변경
            if password:
                user_to_update.set_password(password)

            # 기본 정보 변경
            user_to_update.update_info(full_name=user_update.full_name)

            updated_user = await self.user_repository.update(user=user_to_update)
            return UserRead.model_validate(updated_user)

    async def register_as_seller(self, user_id: int) -> UserRead:
        """사용자를 판매자로 등록(역할 변경)합니다."""
        async with self.uow:
            user = await self.user_repository.get_by_id(user_id=user_id)
            if not user:
                raise UserNotFoundException()

            if user.is_seller:
                raise SellerAlreadyExistsException()

            user.promote_to_seller()
            updated_user = await self.user_repository.update(user=user)
            return UserRead.model_validate(updated_user)
