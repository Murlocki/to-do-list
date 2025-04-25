# Crud юзеров
from sqlalchemy.orm import Session

from src.user_service.auth_functions import get_password_hash
from src.user_service.models import User
from src.user_service.schemas import UserCreate, UserUpdate


def create_user(db: Session, user: UserCreate):
    user_password_hash = get_password_hash(user.password)
    db.add(
        User(
            username=user.username,
            email=str(user.email),
            hashed_password=user_password_hash,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=True,
        )
    )
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user_name:str, user: UserUpdate):
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

def delete_user(db: Session, user_name:str):
    db_user = db.query(User).filter(User.username == user_name).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

def get_user_by_email(db: Session, email:str):
    return db.query(User).filter(User.email == email).first()
def get_user_by_username(db: Session, username:str):
    return db.query(User).filter(User.username == username).first()