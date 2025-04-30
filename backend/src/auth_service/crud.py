# Crud юзеров
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from src.shared import logger_setup
from src.auth_service.auth_functions import get_password_hash, verify_password
from src.auth_service.models import User
from src.auth_service.schemas import UserCreate, UserUpdate

logger = logger_setup.setup_logger(__name__)



# CRUD операции с пользователями
def create_user(db: Session, user: UserCreate):
    user_password_hash = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=str(user.email),
        hashed_password=user_password_hash,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


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


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session):
    return db.query(User).all()

def authenticate_user(db: Session, identifier: str, password: str):
    user = get_user_by_email(db, identifier) or get_user_by_username(db, identifier)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user