from copy import deepcopy
from datetime import timedelta, datetime
from jose import jwt, JWTError

from src.auth_service.kafka_producers import send_kafka_message
from src.shared.schemas import SessionDTO, AccessTokenUpdate
from src.shared.config import settings
from src.auth_service.external_functions import get_session_by_token, update_session_token
from src.shared.logger_setup import setup_logger
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
                             algorithms=settings.jwt_algorithm, options={"verify_exp": False})
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


async def verify_and_refresh_access_token(token: str) -> str | None:
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
        session: SessionDTO = await get_session_by_token(token)
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
            if session.refresh_token:
                # Update session with new access token
                logger.info("Refreshing token using refresh token")
                new_token: str = await refresh_access_token(session.refresh_token)
                # Check if we have new token and update session
                if not new_token:
                    logger.warning("Failed to refresh token")
                    return None
                logger.info("Token refreshed successfully")
                return new_token
            else:
                # Create new access token without refsrh token and update session
                logger.info("Creating new access token")
                new_access_token = create_new_token(payload['sub'])
                if not new_access_token:
                    logger.warning("Failed to create new access token")
                    return None
                session = await update_session_token(session.session_id,
                                     AccessTokenUpdate(old_access_token=token, new_access_token=new_access_token))
                if not session:
                    logger.warning("Failed to update session with new token")
                    return None
                return new_access_token
        logger.info("Token is valid")
        return token
    except JWTError as e:
        logger.warning(f"JWTError: {e}")
        return None


async def refresh_access_token(refresh_token: str):
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
        session = await get_session_by_token(refresh_token, token_type="refresh_token")
        if not session:
            logger.warning(f"No session found for refresh token")
            return None
        new_access_token = create_new_token(email)
        if not new_access_token:
            logger.warning("Failed to create new access token")
            return None

        session = await update_session_token(session.session_id, AccessTokenUpdate(old_access_token=session.access_token,
                                                                      new_access_token=new_access_token))
        if not session:
            logger.warning("Failed to update session with new access token")
            return None
        return new_access_token

    except JWTError as e:
        logger.warning(f"refresh_access_token - JWT Error: {e}")
        return None


async def send_email_signal(access_token:str, user_email:str, message_type:str = "register_email"):
    message = await send_kafka_message({"message_type": message_type,"token": access_token, "email": user_email})

    if not message:
        logger.warning(f"Failed to send {message_type} email")
        return None

    logger.info(f"Send {message_type} email signal sent for {user_email}")
    return message