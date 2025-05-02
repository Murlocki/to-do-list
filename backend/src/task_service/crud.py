# CRUD сессией
import uuid
from datetime import datetime, timedelta

from src.session_service.redis_base import redis_client
from src.shared.config import settings
from src.shared.logger_setup import setup_logger
from src.shared.schemas import SessionDTO

logger = setup_logger(__name__)


async def create_and_store_session(user_id: int, access_token: str, refresh_token: str = None, device: str = "unknown",
                                   ip_address: str = "unknown") -> SessionDTO:
    session_id = str(uuid.uuid4())
    created_at = datetime.now()

    session_data = {
        "session_id": session_id,
        "user_id": user_id,
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
    await redis_client.hset(f"session:{session_id}", mapping=session_data)
    await redis_client.expire(f"session:{session_id}", int((expires_at - created_at).total_seconds()))
    await redis_client.sadd(f"user:{user_id}:sessions", session_id)
    return SessionDTO(**session_data)


async def get_sessions(user_id: int):
    """
    Get all sessions for a user
    :param user_id:
    :return: list of user sessions
    """
    sessions = []
    async for key in redis_client.scan_iter(f"session:*"):
        session_data = await redis_client.hgetall(key)
        if session_data.get("user_id") == str(user_id):
            # Проверяем наличие всех необходимых полей
            required_fields = ["session_id", "user_id", "access_token", "device", "ip_address", "created_at",
                               "expires_at"]
            if all(field in session_data for field in required_fields):
                session_data["created_at"] = datetime.fromisoformat(session_data["created_at"])
                session_data["expires_at"] = datetime.fromisoformat(session_data["expires_at"])
                sessions.append(session_data)
    return sessions


async def delete_inactive_sessions(user_id: int) -> list[str]:
    """
    Delete inactive sessions
    :param user_id: User ID
    :return: list[str]: list of deleted sessions
    """
    result = []
    session_ids = await redis_client.smembers(f"user:{user_id}:sessions")
    for session_id in session_ids:
        session_data = await redis_client.hgetall(f"session:{session_id}")
        if not session_data:
            await redis_client.srem(f"user:{user_id}:sessions", session_id)
            result.append(session_id)
    return result


async def delete_session_by_id(session_id: str) -> SessionDTO | None:
    """
    Delete session by ID
    :param session_id:
    :return: deleted session data
    """
    session_data = await redis_client.hgetall(f"session:{session_id}")
    if session_data:
        await redis_client.delete(f"session:{session_id}")
        await redis_client.srem(f"user:{session_data['user_id']}:sessions", session_id)
        # Проверяем наличие всех необходимых полей
        required_fields = ["session_id", "user_id", "access_token", "device", "ip_address", "created_at", "expires_at"]
        if all(field in session_data for field in required_fields):
            session_data["created_at"] = datetime.fromisoformat(session_data["created_at"])
            session_data["expires_at"] = datetime.fromisoformat(session_data["expires_at"])
            return SessionDTO(**session_data)
    return None


async def get_session_by_token(token: str, token_type: str = "access_token") -> SessionDTO | None:
    """
    Get session by token
    :param token: session token
    :param token_type: access_token or refresh_token
    :return: dict|None
    """
    async for key in redis_client.scan_iter("session:*"):
        session_data = await redis_client.hgetall(key)
        if session_data.get(token_type) == token:
            return SessionDTO(**session_data)
    return None


async def delete_session_by_access_token(token: str, token_type: str = "access_token") -> SessionDTO | None:
    """
    Delete session by token
    :param token: Token
    :param token_type: token type
    :return:
    """
    async for key in redis_client.scan_iter("session:*"):
        session_data = await redis_client.hgetall(key)
        if session_data.get(token_type) == token:
            await redis_client.delete(f"session:{session_data['session_id']}")
            await redis_client.srem(f"user:{session_data['user_id']}:sessions", session_data["session_id"])
            return SessionDTO(**session_data)
    return None


async def update_session_access_token(old_token: str, new_token: str, session_obj: SessionDTO = None)-> SessionDTO | None:
    """
    Update session access token
    :param old_token: Old access token
    :param new_token: New access token
    :param session_obj: Session object
    :return: None
    """
    session = session_obj if session_obj else await get_session_by_token(old_token)
    if session:
        await redis_client.hset(f"session:{session.session_id}", "access_token", new_token)
        session = await get_session_by_token(new_token)
        return session
    return None

async def delete_sessions_by_user_id(user_id: int) -> list[SessionDTO]:
    """
    Delete sessions by user ID
    :param user_id: user ID
    :return: List of deleted sessions
    """
    result = []
    session_ids = await redis_client.smembers(f"user:{user_id}:sessions")
    for session_id in session_ids:
        session_data = await redis_client.hgetall(f"session:{session_id}")
        if session_data:
            await redis_client.delete(f"session:{session_id}", session_id)
            await redis_client.srem(f"user:{user_id}:sessions", session_id)
            result.append(session_id)
    return result