# Crud юзеров
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from src.shared import logger_setup
from src.auth_service.schemas import UserCreate, UserUpdate

logger = logger_setup.setup_logger(__name__)



def update_user(db: Session, user_name: str, user: UserUpdate):
    db_user = db.query(User).filter(User.username == user_name).first()
    if db_user:
        update_data = user.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_name: str):
    db_user = db.query(User).filter(User.username == user_name).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user


def get_users(db: Session):
    return db.query(User).all()

