from fastapi import HTTPException, status

from app.application.dto.token import TokenPayload
from app.application.dto.user_dto import UserCreate, UserRead, UserUpdate
from app.core import security
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
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 등록된 이메일입니다.",
                )

            hashed_password = security.get_password_hash(user_create.password)

            # 도메인 모델 생성
            user_to_create = User(
                email=user_create.email,
                full_name=user_create.full_name,
                hashed_password=hashed_password,
                is_active=True,  # 기본값
            )

            created_user = await self.user_repository.create(user=user_to_create)

            # 응답 DTO로 변환하여 반환
            return UserRead.model_validate(created_user)

    async def login_user(self, email: str, password: str) -> str:
        user = await self.user_repository.get_by_email(email=email)

        # 도메인 모델의 메서드를 사용하여 비밀번호 확인
        if not user or not user.check_password(password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 올바르지 않습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(status_code=400, detail="비활성화된 계정입니다.")

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
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="사용자를 찾을 수 없습니다.",
                )

            update_data = user_update.model_dump(exclude_unset=True)

            if "password" in update_data and update_data["password"]:
                hashed_password = security.get_password_hash(update_data["password"])
                update_data["hashed_password"] = hashed_password

            # 비밀번호 필드는 업데이트 데이터에서 제거 (hashed_password로 대체됨)
            update_data.pop("password", None)

            # 기존 사용자 객체의 복사본을 만들고 업데이트된 데이터 적용
            updated_user_obj = user_to_update.model_copy(update=update_data)

            updated_user = await self.user_repository.update(user=updated_user_obj)
            return UserRead.model_validate(updated_user)

        return UserRead.model_validate(updated_user)
