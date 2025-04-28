# Crud юзеров
import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from src.user_service import logger_setup
from src.user_service.auth_functions import get_password_hash, verify_password
from src.user_service.config import settings
from src.user_service.models import User
from src.user_service.redis_base import redis_client
from src.user_service.schemas import UserCreate, UserUpdate

logger = logger_setup.setup_logger(__name__)


# CRUD сессией
def create_and_store_session(user_id: int, access_token: str, refresh_token: str = None, device: str = "unknown",
                             ip_address: str = "unknown"):
    session_id = str(uuid.uuid4())
    created_at = datetime.now()


    session_data = {
        "session_id": session_id,
        "user_id": str(user_id),
        "access_token": access_token,
        "device": device,
        "ip_address": ip_address,
        "created_at": created_at.isoformat(),
    }
    if refresh_token:
        expires_at = created_at + timedelta(days=settings.refresh_token_expire_days)
        session_data["refresh_token"] = refresh_token
    else:
        expires_at = created_at + timedelta(seconds=settings.access_token_expire_seconds,
                                            minutes=settings.access_token_expire_minutes,
                                            hours=settings.access_token_expire_hours)
    session_data["expires_at"] = expires_at.isoformat()
    logger.info(f"Storing session with expires_at: {expires_at}")

    logger.warning(session_data)
    redis_client.hset(f"session:{session_id}", mapping=session_data)
    redis_client.expire(f"session:{session_id}", int((expires_at - created_at).total_seconds()))
    redis_client.sadd(f"user:{user_id}:sessions", session_id)
    return {k: v for k, v in session_data.items() if k not in ["refresh_token", "access_token"]}


def get_sessions(user_id: int):
    """
    Get all sessions for a user
    :param user_id:
    :return: list of user sessions
    """
    sessions = []
    for key in redis_client.scan_iter(f"session:*"):
        session_data = redis_client.hgetall(key)
        if session_data.get("user_id") == str(user_id):
            # Проверяем наличие всех необходимых полей
            required_fields = ["session_id", "user_id", "access_token", "device", "ip_address", "created_at",
                               "expires_at"]
            if all(field in session_data for field in required_fields):
                session_data["created_at"] = datetime.fromisoformat(session_data["created_at"])
                session_data["expires_at"] = datetime.fromisoformat(session_data["expires_at"])
                sessions.append(session_data)
    return sessions

def delete_inactive_sessions(user_id: int)->list[str]:
    """
    Delete inactive sessions
    :param user_id: User ID
    :return: list[str]: list of deleted sessions
    """
    result = []
    session_ids = redis_client.smembers(f"user:{user_id}:sessions")
    for session_id in session_ids:
        session_data = redis_client.hgetall(f"session:{session_id}")
        if not session_data:
            redis_client.srem(f"user:{user_id}:sessions", session_id)
            result.append(session_id)
    return result

def revoke_session(access_token: str):
    session = redis_client.hgetall(f"session:{access_token}")
    if session:
        refresh_token = session.get("refresh_token")
        redis_client.delete(f"session:{access_token}")
        if refresh_token:
            redis_client.delete(f"refresh:{refresh_token}")


def delete_session_by_id(session_id: str):
    session_data = redis_client.hgetall(f"session:{session_id}")
    if session_data:
        redis_client.delete(f"session:{session_id}")
        redis_client.srem(f"user:{session_data['user_id']}:sessions", session_id)
        # Проверяем наличие всех необходимых полей
        required_fields = ["session_id", "user_id", "access_token", "device", "ip_address", "created_at", "expires_at"]
        if all(field in session_data for field in required_fields):
            session_data["created_at"] = datetime.fromisoformat(session_data["created_at"])
            session_data["expires_at"] = datetime.fromisoformat(session_data["expires_at"])
            return session_data
    return None



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