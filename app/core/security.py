from datetime import UTC, datetime, timedelta
from typing import Annotated

import bcrypt
import jwt
from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.dto.token import TokenPayload
from app.core.config import get_settings
from app.core.exceptions import ForbiddenException
from app.domain.model.seller import Seller
from app.domain.model.user import User, UserRole
from app.domain.ports.user_repository import IUserRepository

settings = get_settings()
security_scheme = HTTPBearer()


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(data: TokenPayload, expires_delta: timedelta | None = None) -> str:
    to_encode = data.model_dump()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    to_encode.update({"exp": expire, "sub": data.sub})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> TokenPayload:
    """
    JWT 토큰을 디코딩하여 페이로드를 반환합니다.

    Args:
        token: 디코딩할 JWT 토큰

    Returns:
        TokenPayload: 토큰 페이로드

    Raises:
        HTTPException: 토큰이 유효하지 않거나 만료된 경우
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@inject
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    user_repository: Annotated[IUserRepository, Depends(Provide["user_repository"])],
) -> User:
    """
    현재 인증된 사용자를 반환합니다.

    Args:
        credentials: HTTP Bearer 인증 정보
        user_repository: 사용자 리포지토리 (DI 컨테이너를 통해 주입)

    Returns:
        User: 현재 인증된 사용자

    Raises:
        HTTPException: 인증에 실패한 경우
    """
    token_data = decode_access_token(credentials.credentials)

    user = await user_repository.get_by_email(token_data.sub)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    return user

async def get_current_seller(
    current_user: Annotated[User, Depends(get_current_user)],
) -> Seller:
    """
    현재 인증된 사용자가 판매자인 경우 판매자 정보를 반환합니다.
    """
    if current_user.role != UserRole.SELLER or not current_user.seller:
        raise ForbiddenException(message="판매자 권한이 필요합니다.")
    
    if current_user.seller.id is None:
        # DB 무결성 상 발생하지 않아야 함
        raise ForbiddenException(message="유효하지 않은 판매자 정보입니다.")

    return current_user.seller
