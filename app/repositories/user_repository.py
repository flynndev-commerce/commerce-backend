from sqlmodel import Session, select

from app.domain.user import UserEntity
from app.schemas.user import UserCreate


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user_create: UserCreate, hashed_password: str) -> UserEntity:
        db_user = UserEntity.model_validate(user_create, update={"hashed_password": hashed_password})
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def get_by_email(self, email: str) -> UserEntity | None:
        statement = select(UserEntity).where(UserEntity.email == email)
        return self.session.exec(statement).first()
