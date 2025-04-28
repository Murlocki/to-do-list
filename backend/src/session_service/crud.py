# CRUD сессией
from datetime import datetime, timedelta
import uuid

from src.session_service.config import settings
from src.session_service.redis_base import redis_client
from src.shared.logger_setup import setup_logger

logger = setup_logger(__name__)




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
    return {k: v for k, v in session_data.items()}


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


def delete_inactive_sessions(user_id: int) -> list[str]:
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

def get_session_by_token(token: str, token_type: str = "access_token") -> dict | None:
    """
    Get session by token
    :param token: session token
    :param token_type: access_token or refresh_token
    :return: dict|None
    """
    # TODO: "Рассмотреть возможность искать сначала по юзеру его сессии и затем по токену нужную выбирать
    #        Возможно это будет хуже,так как могут быть неактивные пользователи без сесссий"

    for key in redis_client.scan_iter("session:*"):
        session_data = redis_client.hgetall(key)
        if session_data.get(token_type) == token:
            return session_data
    return None


def update_session_access_token(old_token: str, new_token: str, session_obj: dict = None):
    """
    Update session access token
    :param old_token: Old access token
    :param new_token: New access token
    :param session_obj: Session object
    :return: None
    """
    session = session_obj if session_obj else get_session_by_token(old_token)
    if session:
        redis_client.hset(f"session:{session['session_id']}", "access_token", new_token)