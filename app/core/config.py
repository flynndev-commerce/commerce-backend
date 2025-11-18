from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    title: str = "Commerce API"
    version: str = "0.1.0"
    debug: bool = False

    # 개발 환경에서만 앱 시작 시 테이블 자동 생성 (운영 환경에서는 False로 설정)
    auto_create_tables: bool = True

    database_url: str = "sqlite+aiosqlite:///:memory:"
    jwt_secret_key: str = "super-secret"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
