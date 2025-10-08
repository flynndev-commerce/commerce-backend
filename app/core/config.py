from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    title: str = "Commerce API"
    version: str = "0.1.0"
    debug: bool = False

    database_url: str = "sqlite:///:memory:"
    jwt_secret_key: str = "super-secret"
    jwt_algorithm: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
