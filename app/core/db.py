from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings

settings = get_settings()

# SQLite에서만 필요한 설정입니다.
connect_args = {"check_same_thread": False}
engine = create_engine(settings.database_url, echo=True, connect_args=connect_args)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
