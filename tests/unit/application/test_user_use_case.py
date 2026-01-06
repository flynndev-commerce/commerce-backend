import pytest

from app.application.dto.user_dto import UserCreate
from app.application.use_cases.user_use_case import UserUseCase
from app.core.exceptions import (
    EmailAlreadyExistsException,
    InvalidCredentialsException,
    UserInactiveException,
)
from app.domain.model.user import User
from tests.fakes.fake_unit_of_work import FakeUnitOfWork
from tests.fakes.repositories.fake_user_repository import FakeUserRepository


@pytest.mark.asyncio
class TestUserUseCase:
    async def test_create_user_success(self) -> None:
        # Given
        user_repo = FakeUserRepository()
        uow = FakeUnitOfWork()
        use_case = UserUseCase(user_repository=user_repo, uow=uow)

        user_create = UserCreate(email="test@example.com", password="password123", full_name="Test User")

        # When
        result = await use_case.create_user(user_create)

        # Then
        assert result.email == "test@example.com"
        assert result.full_name == "Test User"
        assert result.id is not None

        # Repository verification
        saved_user = await user_repo.get_by_email("test@example.com")
        assert saved_user is not None
        assert saved_user.verify_password("password123")

    async def test_create_user_email_already_exists(self) -> None:
        # Given
        user_repo = FakeUserRepository()
        uow = FakeUnitOfWork()
        use_case = UserUseCase(user_repository=user_repo, uow=uow)

        # Pre-populate user
        existing_user = User(
            email="existing@example.com", full_name="Existing User", hashed_password="hashed_password", is_active=True
        )
        await user_repo.create(existing_user)

        user_create = UserCreate(email="existing@example.com", password="password123", full_name="New User")

        # When & Then
        with pytest.raises(EmailAlreadyExistsException):
            await use_case.create_user(user_create)

    async def test_login_user_success(self) -> None:
        # Given
        user_repo = FakeUserRepository()
        uow = FakeUnitOfWork()
        use_case = UserUseCase(user_repository=user_repo, uow=uow)

        # Create user via UseCase to ensure password hashing works correctly
        user_create = UserCreate(email="login@example.com", password="correct_password", full_name="Login User")
        await use_case.create_user(user_create)

        # When
        token = await use_case.login_user("login@example.com", "correct_password")

        # Then
        assert isinstance(token, str)
        assert len(token) > 0

    async def test_login_user_invalid_credentials(self) -> None:
        # Given
        user_repo = FakeUserRepository()
        uow = FakeUnitOfWork()
        use_case = UserUseCase(user_repository=user_repo, uow=uow)

        user_create = UserCreate(email="login@example.com", password="correct_password", full_name="Login User")
        await use_case.create_user(user_create)

        # When & Then (Wrong Password)
        with pytest.raises(InvalidCredentialsException):
            await use_case.login_user("login@example.com", "wrong_password")

    async def test_login_user_not_found(self) -> None:
        # Given
        user_repo = FakeUserRepository()
        uow = FakeUnitOfWork()
        use_case = UserUseCase(user_repository=user_repo, uow=uow)

        # When & Then
        with pytest.raises(InvalidCredentialsException):
            await use_case.login_user("nonexistent@example.com", "password")

    async def test_login_user_inactive(self) -> None:
        # Given
        user_repo = FakeUserRepository()
        uow = FakeUnitOfWork()
        use_case = UserUseCase(user_repository=user_repo, uow=uow)

        inactive_user = User(
            email="inactive@example.com",
            full_name="Inactive User",
            hashed_password="hashed_password",
            is_active=False,  # Inactive
        )
        inactive_user.set_password("password123")
        await user_repo.create(inactive_user)

        # When & Then
        with pytest.raises(UserInactiveException):
            await use_case.login_user("inactive@example.com", "password123")
