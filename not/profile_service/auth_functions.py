import re
from copy import deepcopy
from datetime import timedelta, datetime

from passlib.context import CryptContext
from jose import jwt, JWTError
from src.profile_service.config import settings
from src.shared.logger_setup import setup_logger
from src.profile_service.redis_base import redis_client
import uuid

logger = setup_logger(__name__)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create access token
    :param data: Payload data
    :param expires_delta: Expiration time
    :return: str: JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(seconds=settings.access_token_expire_seconds,
                                            minutes=settings.access_token_expire_minutes,
                                            hours=settings.access_token_expire_hours)
    to_encode.update({"exp": expire.timestamp(), "iat": int(datetime.now().timestamp())})
    logger.info(
        f"Access token created for user: {data['sub']} with expiration: {datetime.fromtimestamp(expire.timestamp())}")
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    logger.info(f"Access token: {encoded_jwt}")
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create refresh token
    :param data: Payload data
    :param expires_delta: Expiration time
    :return: str: JWT token
    """
    to_encode: dict[str, any] = deepcopy(data)
    logger.info(to_encode)
    logger.info(data)
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_refresh, algorithm=settings.jwt_algorithm)
    logger.info(f"Refresh token created for user: {data['sub']} {encoded_jwt}")
    return encoded_jwt


def create_new_token(email: str, is_refresh: bool = False):
    """
    Create new access or refresh token
    :param email: User email for sub header
    :param is_refresh: True if refresh token needs to be created
    :return: str: JWT token
    """
    data = {"iss": "auth-service", "sub": email, "jti": str(uuid.uuid4())}
    return create_refresh_token(data=data) if is_refresh else create_access_token(data=data)


def decode_token(token: str, is_refresh: bool = False) -> dict[str, any] | None:
    """
    Decode token
    :param token: Token for decode
    :param is_refresh: True if it is refresh token
    :return: dict[str, any] | None: Decoded token payload or None if error
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_refresh if is_refresh else settings.jwt_secret,
                             algorithms=settings.jwt_algorithm)
        logger.info(f"Token decoded successfully: {payload}")
        return payload
    except JWTError as e:
        logger.warning(f"JWTError: {e}")
        return None


def is_about_to_expire(exp_time: datetime, threshold: int = 300) -> bool:
    """
    Check if token is about to expire
    :param exp_time:
    :param threshold:
    :return: bool
    """
    time_left = (exp_time - datetime.now()).total_seconds()
    logger.info(f"check: time left until token expiration: {time_left} seconds")
    return time_left < threshold


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



def verify_and_refresh_access_token(token: str)->str | None:
    """
    Verify and refresh access token
    :param token: Access token
    :return:str | None: New access token or None if error
    """
    try:

        # Check if the token is a decoded JWT
        payload: dict[str, any] | None = decode_token(token)
        if not payload:
            logger.warning("Token verification failed")
            return None

        # Check if we have session for token
        session: dict | None = get_session_by_token(token)
        if not session:
            logger.warning(f"No session found for token")
            return None

        # Check token exp time
        exp_time: datetime = datetime.fromtimestamp(payload.get("exp"))
        logger.info(f"Token expires at: {exp_time}")
        about_to_expire: bool = is_about_to_expire(exp_time)

        if about_to_expire or exp_time <= datetime.now():
            logger.warning("Token is about to expire" if about_to_expire else f"Token expired at: {exp_time}")
            # Check if we have refresh token
            if "refresh_token" in session:
                # Update session with new access token
                logger.info("Refreshing token using refresh token")
                new_token: str = refresh_access_token(session["refresh_token"])
                # Check if we have new token and update session
                if new_token:
                    logger.info("Token refreshed successfully")
                    update_session_access_token(token, new_token, session)
                    return new_token
                else:
                    logger.warning("Failed to refresh token")
            else:
                # Create new access token without refsrh token and update session
                logger.info("Creating new access token")
                new_access_token = create_new_token(payload['sub'])
                update_session_access_token(token, new_access_token, session)
                return new_access_token
        logger.info("Token is valid")
        return token
    except JWTError as e:
        logger.warning(f"JWTError: {e}")
        return None


def refresh_access_token(refresh_token: str):
    """
    Refresh access token using refresh token
    :param refresh_token: Refresh token
    :return: str | None: New access token or None if error
    """
    try:
        payload = decode_token(refresh_token, is_refresh=True)
        if not refresh_token:
            logger.warning("Refresh token is not valid or has expired")
            return None
        if not payload:
            logger.warning("Invalid refresh token")
            return None
        email = payload.get("sub")
        if not email:
            logger.warning("No email in refresh token payload")
            return None

        # Получаем сессию по refresh token
        session = get_session_by_token(refresh_token, token_type="refresh_token")
        if not session:
            logger.warning(f"No session found for refresh token")
            return None
        new_access_token = create_new_token(email, is_refresh=True)
        update_session_access_token(session.get("access_token"), new_access_token)
        return new_access_token
    except JWTError as e:
        logger.warning(f"refresh_access_token - JWT Error: {e}")
        return None



def validate_password(password: str) -> bool:
    return re.search("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*=])[A-Za-z\d!@#$%^&*=]{8,}$", password) is not None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
