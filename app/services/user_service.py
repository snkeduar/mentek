from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserInDB
from app.repositories.user import UserRepository

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def get_user(self, db: Session, user_id: int) -> Optional[UserInDB]:
        db_user = self.user_repository.get(db, id=user_id)
        if db_user:
            return UserInDB.from_orm(db_user)
        return None

    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> list[UserInDB]:
        db_users = self.user_repository.get_multi(db, skip=skip, limit=limit)
        return [UserInDB.from_orm(user) for user in db_users]

    def create_user(self, db: Session, user_create: UserCreate) -> UserInDB:
        db_user = self.user_repository.create(db, obj_in=user_create)
        return UserInDB.from_orm(db_user)

    def update_user(
        self, db: Session, user_id: int, user_update: UserUpdate
    ) -> Optional[UserInDB]:
        db_user = self.user_repository.get(db, id=user_id)
        if not db_user:
            return None
        updated_user = self.user_repository.update(db, db_obj=db_user, obj_in=user_update)
        return UserInDB.from_orm(updated_user)

    def delete_user(self, db: Session, user_id: int) -> Optional[UserInDB]:
        db_user = self.user_repository.get(db, id=user_id)
        if not db_user:
            return None
        deleted_user = self.user_repository.delete(db, id=user_id)
        return UserInDB.from_orm(deleted_user)